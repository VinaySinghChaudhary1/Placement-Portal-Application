# backend/application/routes_admin.py
from datetime import datetime
from flask import Blueprint, request, current_app as app
from sqlalchemy import or_

from application.models import (
    db, User, StudentProfile, CompanyProfile, PlacementDrive, Application,
    ApprovalStatus, DriveStatus, ApplicationStatus, Notification, PortalVisit,
)
from application.auth_utils import role_required, paginate_args, validate_password_strength
from flask_security import hash_password, current_user
from application.cache import cache

admin_bp = Blueprint("admin_bp", __name__, url_prefix="/api/admin")


def _notify(user_id, title, message, ntype="system", link=None):
    db.session.add(Notification(user_id=user_id, title=title, message=message, type=ntype, link=link))


def _bust_dashboard_cache():
    cache.delete("admin_dashboard_stats")
    cache.delete("approved_drives_list")


@admin_bp.route("/dashboard", methods=["GET"])
@role_required("admin")
def dashboard():
    stats = cache.get("admin_dashboard_stats")
    if stats is None:
        stats = {
            "total_students": StudentProfile.query.count(),
            "total_companies": CompanyProfile.query.count(),
            "pending_companies": CompanyProfile.query.filter_by(approval_status=ApprovalStatus.PENDING).count(),
            "total_drives": PlacementDrive.query.count(),
            "pending_drives": PlacementDrive.query.filter_by(status=DriveStatus.PENDING).count(),
            "approved_drives": PlacementDrive.query.filter_by(status=DriveStatus.APPROVED).count(),
            "total_applications": Application.query.count(),
            "total_selected": Application.query.filter_by(status=ApplicationStatus.SELECTED).count(),
        }
        cache.set("admin_dashboard_stats", stats, timeout=30)
    return {"stats": stats}, 200


# ---------------------------------------------------------------- companies
@admin_bp.route("/companies", methods=["GET"])
@role_required("admin")
def list_companies():
    q = CompanyProfile.query
    status = request.args.get("status")
    search = request.args.get("search")
    if status:
        try:
            q = q.filter_by(approval_status=ApprovalStatus(status))
        except ValueError:
            pass
    if search:
        like = f"%{search}%"
        q = q.join(User).filter(or_(CompanyProfile.company_name.ilike(like), User.email.ilike(like)))
    page, per_page = paginate_args()
    pager = q.order_by(CompanyProfile.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [c.to_dict(include_counts=True) for c in pager.items],
        "total": pager.total, "page": page, "pages": pager.pages,
    }, 200


@admin_bp.route("/companies/<int:company_id>/approve", methods=["POST"])
@role_required("admin")
def approve_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = ApprovalStatus.APPROVED
    company.rejection_reason = None
    _notify(company.user_id, "Company approved",
            "Your company registration has been approved. You can now create placement drives.",
            "status_update")
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Company approved.", "company": company.to_dict()}, 200


@admin_bp.route("/companies/<int:company_id>/reject", methods=["POST"])
@role_required("admin")
def reject_company(company_id):
    data = request.get_json(silent=True) or {}
    company = CompanyProfile.query.get_or_404(company_id)
    company.approval_status = ApprovalStatus.REJECTED
    company.rejection_reason = data.get("reason", "Does not meet institute criteria.")
    _notify(company.user_id, "Company registration rejected", company.rejection_reason, "status_update")
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Company rejected.", "company": company.to_dict()}, 200


@admin_bp.route("/companies/<int:company_id>", methods=["GET", "PUT"])
@role_required("admin")
def company_detail(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    if request.method == "GET":
        return {"company": company.to_dict(include_counts=True)}, 200

    data = request.get_json(silent=True) or {}
    user = company.user

    if "email" in data and data["email"]:
        new_email = data["email"].strip().lower()
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return {"message": "That email is already registered to another account."}, 409
        user.email = new_email
    if "username" in data and data["username"]:
        new_username = data["username"].strip()
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            return {"message": "That username is already taken."}, 409
        user.username = new_username
    if data.get("password"):
        err = validate_password_strength(data["password"])
        if err:
            return {"message": err}, 400
        user.password = hash_password(data["password"])

    for field in ("company_name", "hr_contact_name", "hr_email", "hr_phone", "website",
                  "description", "industry"):
        if field in data:
            setattr(company, field, data[field])

    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Company profile updated.", "company": company.to_dict(include_counts=True)}, 200


@admin_bp.route("/companies/<int:company_id>/reports", methods=["GET"])
@role_required("admin")
def company_reports(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    from application.report_utils import bucket_by_month

    drives = company.drives
    all_applications = [a for d in drives for a in d.applications]

    monthly_drives = bucket_by_month([d.created_at for d in drives])
    monthly_applications = bucket_by_month([a.applied_at for a in all_applications])

    status_breakdown = {}
    for a in all_applications:
        key = a.status.value if a.status else "unknown"
        status_breakdown[key] = status_breakdown.get(key, 0) + 1

    top_drives = sorted(drives, key=lambda d: len(d.applications), reverse=True)[:5]
    top_drives = [{"job_title": d.job_title, "count": len(d.applications)} for d in top_drives if d.applications]

    return {
        "company": company.to_dict(include_counts=True),
        "monthly_drives": monthly_drives,
        "monthly_applications": monthly_applications,
        "status_breakdown": status_breakdown,
        "top_drives": top_drives,
    }, 200


@admin_bp.route("/companies/<int:company_id>/blacklist", methods=["POST"])
@role_required("admin")
def blacklist_company(company_id):
    data = request.get_json(silent=True) or {}
    company = CompanyProfile.query.get_or_404(company_id)
    company.blacklisted = bool(data.get("blacklisted", True))
    company.blacklist_reason = data.get("reason") if company.blacklisted else None
    if company.blacklisted:
        # cancel all of its pending/approved drives so students stop seeing them
        for drive in company.drives:
            if drive.status in (DriveStatus.PENDING, DriveStatus.APPROVED):
                drive.status = DriveStatus.CLOSED
        _notify(company.user_id, "Company blacklisted",
                data.get("reason") or "Your company has been blacklisted by the admin.", "status_update")
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Updated.", "company": company.to_dict()}, 200


@admin_bp.route("/companies/<int:company_id>/deactivate", methods=["POST"])
@role_required("admin")
def toggle_company_user(company_id):
    data = request.get_json(silent=True) or {}
    company = CompanyProfile.query.get_or_404(company_id)
    company.user.active = bool(data.get("active", False))
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Updated.", "company": company.to_dict()}, 200


# ---------------------------------------------------------------- students
@admin_bp.route("/students", methods=["GET"])
@role_required("admin")
def list_students():
    q = StudentProfile.query
    search = request.args.get("search")
    branch = request.args.get("branch")
    if search:
        like = f"%{search}%"
        q = q.join(User).filter(or_(StudentProfile.full_name.ilike(like), User.email.ilike(like)))
    if branch:
        q = q.filter(StudentProfile.branch == branch)
    page, per_page = paginate_args()
    pager = q.order_by(StudentProfile.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [s.to_dict() for s in pager.items],
        "total": pager.total, "page": page, "pages": pager.pages,
    }, 200


@admin_bp.route("/students/<int:student_id>", methods=["GET", "PUT"])
@role_required("admin")
def student_detail(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    if request.method == "GET":
        return {"student": student.to_dict()}, 200

    data = request.get_json(silent=True) or {}
    user = student.user

    if "email" in data and data["email"]:
        new_email = data["email"].strip().lower()
        if new_email != user.email and User.query.filter_by(email=new_email).first():
            return {"message": "That email is already registered to another account."}, 409
        user.email = new_email
    if "username" in data and data["username"]:
        new_username = data["username"].strip()
        if new_username != user.username and User.query.filter_by(username=new_username).first():
            return {"message": "That username is already taken."}, 409
        user.username = new_username
    if data.get("password"):
        err = validate_password_strength(data["password"])
        if err:
            return {"message": err}, 400
        user.password = hash_password(data["password"])

    for field in ("full_name", "branch", "phone"):
        if field in data:
            setattr(student, field, data[field])
    if "year" in data and data["year"] not in (None, ""):
        try:
            student.year = int(data["year"])
        except (TypeError, ValueError):
            return {"message": "year must be an integer."}, 400
    if "cgpa" in data and data["cgpa"] not in (None, ""):
        try:
            cgpa = float(data["cgpa"])
        except (TypeError, ValueError):
            return {"message": "cgpa must be a number."}, 400
        if cgpa < 0 or cgpa > 10:
            return {"message": "CGPA must be between 0 and 10."}, 400
        student.cgpa = cgpa

    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Student profile updated.", "student": student.to_dict()}, 200


@admin_bp.route("/students/<int:student_id>/reports", methods=["GET"])
@role_required("admin")
def student_reports(student_id):
    student = StudentProfile.query.get_or_404(student_id)
    from application.report_utils import bucket_by_month

    monthly_applications = bucket_by_month([a.applied_at for a in student.applications])
    status_breakdown = {}
    for a in student.applications:
        key = a.status.value if a.status else "unknown"
        status_breakdown[key] = status_breakdown.get(key, 0) + 1

    return {
        "student": student.to_dict(),
        "monthly_applications": monthly_applications,
        "status_breakdown": status_breakdown,
    }, 200


@admin_bp.route("/students/<int:student_id>/blacklist", methods=["POST"])
@role_required("admin")
def blacklist_student(student_id):
    data = request.get_json(silent=True) or {}
    student = StudentProfile.query.get_or_404(student_id)
    student.blacklisted = bool(data.get("blacklisted", True))
    student.blacklist_reason = data.get("reason") if student.blacklisted else None
    if student.blacklisted:
        _notify(student.user_id, "Account blacklisted",
                data.get("reason") or "You have been blacklisted by the admin.", "status_update")
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Updated.", "student": student.to_dict()}, 200


@admin_bp.route("/students/<int:student_id>/deactivate", methods=["POST"])
@role_required("admin")
def toggle_student_user(student_id):
    data = request.get_json(silent=True) or {}
    student = StudentProfile.query.get_or_404(student_id)
    student.user.active = bool(data.get("active", False))
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Updated.", "student": student.to_dict()}, 200


# ---------------------------------------------------------------- drives
@admin_bp.route("/drives", methods=["GET"])
@role_required("admin")
def list_drives():
    q = PlacementDrive.query
    status = request.args.get("status")
    search = request.args.get("search")
    if status:
        try:
            q = q.filter_by(status=DriveStatus(status))
        except ValueError:
            pass
    if search:
        like = f"%{search}%"
        q = q.join(CompanyProfile).filter(or_(PlacementDrive.job_title.ilike(like),
                                                CompanyProfile.company_name.ilike(like)))
    page, per_page = paginate_args()
    pager = q.order_by(PlacementDrive.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [d.to_dict(include_applicant_count=True) for d in pager.items],
        "total": pager.total, "page": page, "pages": pager.pages,
    }, 200


@admin_bp.route("/drives/<int:drive_id>/approve", methods=["POST"])
@role_required("admin")
def approve_drive(drive_id):
    drive = PlacementDrive.query.get_or_404(drive_id)
    if drive.company.blacklisted:
        return {"message": "Cannot approve a drive from a blacklisted company."}, 400
    drive.status = DriveStatus.APPROVED
    drive.rejection_reason = None
    _notify(drive.company.user_id, "Drive approved", f"Your drive '{drive.job_title}' is now live.", "status_update")
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Drive approved.", "drive": drive.to_dict()}, 200


@admin_bp.route("/drives/<int:drive_id>/reject", methods=["POST"])
@role_required("admin")
def reject_drive(drive_id):
    data = request.get_json(silent=True) or {}
    drive = PlacementDrive.query.get_or_404(drive_id)
    drive.status = DriveStatus.REJECTED
    drive.rejection_reason = data.get("reason", "Does not meet institute guidelines.")
    _notify(drive.company.user_id, "Drive rejected", f"'{drive.job_title}': {drive.rejection_reason}", "status_update")
    db.session.commit()
    _bust_dashboard_cache()
    return {"message": "Drive rejected.", "drive": drive.to_dict()}, 200


# ---------------------------------------------------------------- applications (read-only, institute-wide)
@admin_bp.route("/applications", methods=["GET"])
@role_required("admin")
def list_all_applications():
    q = Application.query
    status = request.args.get("status")
    if status:
        try:
            q = q.filter_by(status=ApplicationStatus(status))
        except ValueError:
            pass
    page, per_page = paginate_args()
    pager = q.order_by(Application.applied_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return {
        "items": [a.to_dict(include_student=True, include_drive=True) for a in pager.items],
        "total": pager.total, "page": page, "pages": pager.pages,
    }, 200


# ---------------------------------------------------------------- search
@admin_bp.route("/search", methods=["GET"])
@role_required("admin")
def admin_search():
    query = request.args.get("q", "").strip()
    if not query:
        return {"companies": [], "students": []}, 200
    like = f"%{query}%"
    companies = (CompanyProfile.query.filter(CompanyProfile.company_name.ilike(like)).limit(10).all())
    students = (StudentProfile.query.filter(StudentProfile.full_name.ilike(like)).limit(10).all())
    return {
        "companies": [c.to_dict() for c in companies],
        "students": [s.to_dict() for s in students],
    }, 200


# ---------------------------------------------------------------- settings (scheduler config)
@admin_bp.route("/settings", methods=["GET", "PUT"])
@role_required("admin")
def settings():
    from application.models import SystemSetting
    keys = ["daily_reminder_hour", "daily_reminder_minute", "daily_reminder_window_days",
            "monthly_report_day", "monthly_report_hour", "monthly_report_minute"]
    if request.method == "GET":
        return {k: SystemSetting.get_value(k) for k in keys}, 200
    data = request.get_json(silent=True) or {}
    for k in keys:
        if k in data:
            SystemSetting.set_value(k, data[k])
    return {"message": "Settings updated.", **{k: SystemSetting.get_value(k) for k in keys}}, 200


# ---------------------------------------------------------------- reports
@admin_bp.route("/reports/monthly", methods=["GET"])
@role_required("admin")
def monthly_report_preview():
    from application.tasks_monthly import build_monthly_report_data, latest_activity_month
    year = request.args.get("year", type=int)
    month = request.args.get("month", type=int)
    # No explicit month requested: open on the newest month that has activity
    # rather than a blank current month.
    if not (year and month):
        year, month = latest_activity_month()
    data = build_monthly_report_data(year=year, month=month)
    return {"report": data}, 200


@admin_bp.route("/reports/monthly/trigger", methods=["POST"])
@role_required("admin")
def trigger_monthly_report():
    from application.tasks_monthly import send_monthly_report
    task = send_monthly_report.delay()
    return {"message": "Monthly report generation started.", "task_id": task.id}, 202


@admin_bp.route("/reports/overview", methods=["GET"])
@role_required("admin")
def reports_overview():
    from application.report_utils import bucket_by_month

    monthly_applications = bucket_by_month([a.applied_at for a in Application.query.all()])
    student_visits = PortalVisit.query.filter_by(role="student").all()
    monthly_visits = bucket_by_month([v.created_at for v in student_visits])

    companies = CompanyProfile.query.all()
    ranked = sorted(companies, key=lambda c: sum(len(d.applications) for d in c.drives), reverse=True)
    top_companies = [
        {"company_name": c.company_name, "count": sum(len(d.applications) for d in c.drives)}
        for c in ranked[:5] if sum(len(d.applications) for d in c.drives) > 0
    ]

    return {
        "monthly_applications": monthly_applications,
        "monthly_visits": monthly_visits,
        "top_companies": top_companies,
    }, 200


@admin_bp.route("/reminders/trigger", methods=["POST"])
@role_required("admin")
def trigger_reminders():
    from application.tasks_reminder import send_deadline_reminders
    task = send_deadline_reminders.delay()
    return {"message": "Deadline reminder job started.", "task_id": task.id}, 202


# ---------------------------------------------------------------- full data export
@admin_bp.route("/export-csv", methods=["POST"])
@role_required("admin")
def export_csv():
    from application.tasks_export import generate_admin_export_csv
    task = generate_admin_export_csv.delay(current_user.id)
    return {"message": "Export started. You'll be notified when it's ready.", "task_id": task.id}, 202


@admin_bp.route("/export-status/<task_id>", methods=["GET"])
@role_required("admin")
def export_status(task_id):
    from application.celery_init import celery_init_app  # noqa: F401 (ensures celery configured)
    from app import celery
    result = celery.AsyncResult(task_id)
    payload = {"task_id": task_id, "state": result.state}
    if result.state == "SUCCESS":
        payload["filename"] = result.result
    elif result.state == "FAILURE":
        payload["error"] = str(result.result)
    return payload, 200
