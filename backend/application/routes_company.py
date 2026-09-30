# backend/application/routes_company.py
from datetime import datetime
from flask import Blueprint, request, current_app as app
from flask_security import current_user

from application.models import (
    db, CompanyProfile, PlacementDrive, Application, Interview,
    ApprovalStatus, DriveStatus, ApplicationStatus, InterviewMode, InterviewResult, Notification,
)
from application.auth_utils import role_required, paginate_args
from application.cache import cache

company_bp = Blueprint("company_bp", __name__, url_prefix="/api/company")


def _notify(user_id, title, message, ntype="system", link=None):
    db.session.add(Notification(user_id=user_id, title=title, message=message, type=ntype, link=link))


def _my_company():
    return CompanyProfile.query.filter_by(user_id=current_user.id).first()


def _require_company():
    company = _my_company()
    if not company:
        return None, ({"message": "Company profile not found."}, 404)
    return company, None


@company_bp.route("/profile", methods=["GET", "PUT"])
@role_required("company")
def profile():
    company, err = _require_company()
    if err:
        return err
    if request.method == "GET":
        return {"profile": company.to_dict()}, 200
    data = request.get_json(silent=True) or {}
    for field in ("company_name", "hr_contact_name", "hr_email", "hr_phone", "website",
                  "description", "industry"):
        if field in data:
            setattr(company, field, data[field])
    db.session.commit()
    return {"message": "Profile updated.", "profile": company.to_dict()}, 200


@company_bp.route("/dashboard", methods=["GET"])
@role_required("company")
def dashboard():
    company, err = _require_company()
    if err:
        return err
    drives = PlacementDrive.query.filter_by(company_id=company.id).order_by(PlacementDrive.created_at.desc()).all()
    total_applicants = sum(len(d.applications) for d in drives)
    return {
        "profile": company.to_dict(),
        "stats": {
            "total_drives": len(drives),
            "approved_drives": len([d for d in drives if d.status == DriveStatus.APPROVED]),
            "pending_drives": len([d for d in drives if d.status == DriveStatus.PENDING]),
            "closed_drives": len([d for d in drives if d.status == DriveStatus.CLOSED]),
            "total_applicants": total_applicants,
        },
        "drives": [d.to_dict(include_applicant_count=True) for d in drives],
    }, 200


@company_bp.route("/drives", methods=["GET", "POST"])
@role_required("company")
def drives():
    company, err = _require_company()
    if err:
        return err

    if request.method == "GET":
        q = PlacementDrive.query.filter_by(company_id=company.id)
        status = request.args.get("status")
        if status:
            try:
                q = q.filter_by(status=DriveStatus(status))
            except ValueError:
                pass
        items = q.order_by(PlacementDrive.created_at.desc()).all()
        return {"items": [d.to_dict(include_applicant_count=True) for d in items]}, 200

    # POST -> create new drive (goes to admin approval queue)
    if company.approval_status != ApprovalStatus.APPROVED:
        return {"message": "Your company must be approved by the admin before creating drives."}, 403
    if company.blacklisted:
        return {"message": "Your company has been blacklisted and cannot create drives."}, 403

    data = request.get_json(silent=True) or {}
    required = ["job_title", "job_description", "application_deadline"]
    if not all(data.get(f) for f in required):
        return {"message": "job_title, job_description and application_deadline are required."}, 400
    try:
        deadline = datetime.strptime(data["application_deadline"], "%Y-%m-%dT%H:%M") \
            if "T" in data["application_deadline"] else datetime.strptime(data["application_deadline"], "%Y-%m-%d %H:%M")
    except ValueError:
        return {"message": "application_deadline must be an ISO datetime (YYYY-MM-DDTHH:MM)."}, 400
    if deadline <= datetime.utcnow():
        return {"message": "application_deadline must be in the future."}, 400

    drive = PlacementDrive(
        company_id=company.id,
        job_title=data["job_title"],
        job_description=data["job_description"],
        eligible_branches=",".join(data.get("eligible_branches", []) or []) if isinstance(data.get("eligible_branches"), list) else (data.get("eligible_branches") or ""),
        eligible_years=",".join(str(y) for y in data.get("eligible_years", []) or []) if isinstance(data.get("eligible_years"), list) else (data.get("eligible_years") or ""),
        min_cgpa=float(data.get("min_cgpa") or 0),
        salary_package=float(data["salary_package"]) if data.get("salary_package") not in (None, "") else None,
        location=data.get("location"),
        application_deadline=deadline,
        status=DriveStatus.PENDING,
    )
    db.session.add(drive)
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    return {"message": "Drive submitted for admin approval.", "drive": drive.to_dict()}, 201


@company_bp.route("/drives/<int:drive_id>", methods=["GET", "PUT"])
@role_required("company")
def drive_detail(drive_id):
    company, err = _require_company()
    if err:
        return err
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return {"message": "Drive not found."}, 404

    if request.method == "GET":
        return {"drive": drive.to_dict(include_applicant_count=True)}, 200

    if drive.status not in (DriveStatus.PENDING, DriveStatus.APPROVED):
        return {"message": "Closed or rejected drives cannot be edited."}, 400
    data = request.get_json(silent=True) or {}
    for field in ("job_title", "job_description", "location"):
        if field in data:
            setattr(drive, field, data[field])
    if "min_cgpa" in data:
        drive.min_cgpa = float(data["min_cgpa"] or 0)
    if "salary_package" in data:
        drive.salary_package = float(data["salary_package"]) if data["salary_package"] not in (None, "") else None
    if "eligible_branches" in data:
        val = data["eligible_branches"]
        drive.eligible_branches = ",".join(val) if isinstance(val, list) else (val or "")
    if "eligible_years" in data:
        val = data["eligible_years"]
        drive.eligible_years = ",".join(str(y) for y in val) if isinstance(val, list) else (val or "")
    if data.get("application_deadline"):
        try:
            raw = data["application_deadline"]
            drive.application_deadline = datetime.strptime(raw, "%Y-%m-%dT%H:%M") if "T" in raw else datetime.strptime(raw, "%Y-%m-%d %H:%M")
        except ValueError:
            return {"message": "Invalid application_deadline format."}, 400
    # editing an approved drive sends it back for re-approval, matching admin oversight requirement
    if drive.status == DriveStatus.APPROVED:
        drive.status = DriveStatus.PENDING
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    return {"message": "Drive updated and resubmitted for approval.", "drive": drive.to_dict()}, 200


@company_bp.route("/drives/<int:drive_id>/close", methods=["POST"])
@role_required("company")
def close_drive(drive_id):
    company, err = _require_company()
    if err:
        return err
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return {"message": "Drive not found."}, 404
    drive.status = DriveStatus.CLOSED
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    return {"message": "Drive marked as complete/closed.", "drive": drive.to_dict()}, 200


@company_bp.route("/drives/<int:drive_id>/applications", methods=["GET"])
@role_required("company")
def drive_applications(drive_id):
    company, err = _require_company()
    if err:
        return err
    drive = PlacementDrive.query.filter_by(id=drive_id, company_id=company.id).first()
    if not drive:
        return {"message": "Drive not found."}, 404
    apps = Application.query.filter_by(drive_id=drive.id).order_by(Application.applied_at.desc()).all()
    return {"drive": drive.to_dict(), "applications": [a.to_dict(include_student=True) for a in apps]}, 200


@company_bp.route("/applications/<int:application_id>/status", methods=["POST"])
@role_required("company")
def update_application_status(application_id):
    company, err = _require_company()
    if err:
        return err
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return {"message": "You don't have access to this application."}, 403

    data = request.get_json(silent=True) or {}
    new_status = data.get("status")
    try:
        application.status = ApplicationStatus(new_status)
    except (ValueError, TypeError):
        valid = [s.value for s in ApplicationStatus]
        return {"message": f"status must be one of {valid}"}, 400

    db.session.commit()
    _notify(application.student.user_id, "Application status updated",
            f"Your application for '{application.drive.job_title}' at {company.company_name} is now: {application.status.value.replace('_', ' ')}.",
            "status_update")
    db.session.commit()
    return {"message": "Application status updated.", "application": application.to_dict()}, 200


@company_bp.route("/applications/<int:application_id>/interview", methods=["POST"])
@role_required("company")
def schedule_interview(application_id):
    company, err = _require_company()
    if err:
        return err
    application = Application.query.get_or_404(application_id)
    if application.drive.company_id != company.id:
        return {"message": "You don't have access to this application."}, 403

    data = request.get_json(silent=True) or {}
    if not data.get("scheduled_at"):
        return {"message": "scheduled_at is required."}, 400
    try:
        raw = data["scheduled_at"]
        scheduled_at = datetime.strptime(raw, "%Y-%m-%dT%H:%M") if "T" in raw else datetime.strptime(raw, "%Y-%m-%d %H:%M")
    except ValueError:
        return {"message": "Invalid scheduled_at format."}, 400

    interview = Interview(
        application_id=application.id,
        round_name=data.get("round_name", "Interview"),
        scheduled_at=scheduled_at,
        mode=InterviewMode(data.get("mode", "online")) if data.get("mode") in ("online", "offline") else InterviewMode.ONLINE,
        location_or_link=data.get("location_or_link"),
        remarks=data.get("remarks"),
        result=InterviewResult.PENDING,
    )
    db.session.add(interview)
    application.status = ApplicationStatus.INTERVIEW_SCHEDULED
    db.session.commit()
    _notify(application.student.user_id, "Interview scheduled",
            f"An interview round '{interview.round_name}' has been scheduled for '{application.drive.job_title}' at {company.company_name} on {interview.scheduled_at.strftime('%Y-%m-%d %H:%M')}.",
            "interview")
    db.session.commit()
    return {"message": "Interview scheduled.", "interview": interview.to_dict()}, 201


@company_bp.route("/reports", methods=["GET"])
@role_required("company")
def reports():
    company, err = _require_company()
    if err:
        return err
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
        "monthly_drives": monthly_drives,
        "monthly_applications": monthly_applications,
        "status_breakdown": status_breakdown,
        "top_drives": top_drives,
    }, 200


@company_bp.route("/export-csv", methods=["POST"])
@role_required("company")
def export_csv():
    company, err = _require_company()
    if err:
        return err
    from application.tasks_export import generate_company_report_csv
    task = generate_company_report_csv.delay(company.id)
    return {"message": "Export started. You'll be notified when it's ready.", "task_id": task.id}, 202


@company_bp.route("/export-status/<task_id>", methods=["GET"])
@role_required("company")
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


@company_bp.route("/interviews/<int:interview_id>/result", methods=["POST"])
@role_required("company")
def update_interview_result(interview_id):
    company, err = _require_company()
    if err:
        return err
    interview = Interview.query.get_or_404(interview_id)
    if interview.application.drive.company_id != company.id:
        return {"message": "You don't have access to this interview."}, 403
    data = request.get_json(silent=True) or {}
    try:
        interview.result = InterviewResult(data.get("result"))
    except (ValueError, TypeError):
        return {"message": "result must be one of pending/cleared/not_cleared."}, 400
    interview.remarks = data.get("remarks", interview.remarks)
    db.session.commit()
    return {"message": "Interview result updated.", "interview": interview.to_dict()}, 200
