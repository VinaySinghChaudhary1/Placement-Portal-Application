# backend/application/routes_student.py
import os
from datetime import datetime
from flask import Blueprint, request, current_app as app, send_from_directory
from flask_security import current_user
from werkzeug.utils import secure_filename

from application.models import (
    db, StudentProfile, PlacementDrive, Application, DriveStatus, ApplicationStatus,
    Notification,
)
from application.auth_utils import role_required, paginate_args
from application.cache import cache

student_bp = Blueprint("student_bp", __name__, url_prefix="/api/student")


def _notify(user_id, title, message, ntype="system", link=None):
    db.session.add(Notification(user_id=user_id, title=title, message=message, type=ntype, link=link))


def _my_student():
    return StudentProfile.query.filter_by(user_id=current_user.id).first()


def _require_student():
    student = _my_student()
    if not student:
        return None, ({"message": "Student profile not found."}, 404)
    return student, None


@student_bp.route("/profile", methods=["GET", "PUT"])
@role_required("student")
def profile():
    student, err = _require_student()
    if err:
        return err
    if request.method == "GET":
        return {"profile": student.to_dict()}, 200
    data = request.get_json(silent=True) or {}
    for field in ("full_name", "branch", "phone"):
        if field in data:
            setattr(student, field, data[field])
    if "year" in data:
        try:
            student.year = int(data["year"])
        except (TypeError, ValueError):
            return {"message": "year must be an integer."}, 400
    if "cgpa" in data:
        try:
            cgpa = float(data["cgpa"])
            if cgpa < 0 or cgpa > 10:
                raise ValueError
            student.cgpa = cgpa
        except (TypeError, ValueError):
            return {"message": "cgpa must be a number between 0 and 10."}, 400
    db.session.commit()
    return {"message": "Profile updated.", "profile": student.to_dict()}, 200


@student_bp.route("/resume", methods=["POST"])
@role_required("student")
def upload_resume():
    student, err = _require_student()
    if err:
        return err
    if "resume" not in request.files:
        return {"message": "No file part named 'resume' in the request."}, 400
    file = request.files["resume"]
    if not file or file.filename == "":
        return {"message": "No file selected."}, 400
    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in app.config["ALLOWED_RESUME_EXTENSIONS"]:
        return {"message": "Only PDF, DOC and DOCX resumes are allowed."}, 400

    filename = secure_filename(f"student_{student.id}_{int(datetime.utcnow().timestamp())}.{ext}")
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(filepath)

    student.resume_path = filepath
    student.resume_filename = file.filename
    db.session.commit()
    return {"message": "Resume uploaded.", "profile": student.to_dict()}, 200


@student_bp.route("/resume", methods=["GET"])
@role_required("student")
def download_own_resume():
    student, err = _require_student()
    if err:
        return err
    if not student.resume_path or not os.path.exists(student.resume_path):
        return {"message": "No resume on file."}, 404
    directory, filename = os.path.split(student.resume_path)
    return send_from_directory(directory, filename, as_attachment=True,
                                download_name=student.resume_filename or filename)


@student_bp.route("/drives", methods=["GET"])
@role_required("student")
def browse_drives():
    student, err = _require_student()
    if err:
        return err

    cache_key = "approved_drives_list"
    items = cache.get(cache_key)
    if items is None:
        drives = PlacementDrive.query.filter_by(status=DriveStatus.APPROVED) \
            .order_by(PlacementDrive.application_deadline.asc()).all()
        items = [d.to_dict(include_applicant_count=False) for d in drives]
        cache.set(cache_key, items, timeout=30)

    search = request.args.get("search", "").strip().lower()
    eligible_only = request.args.get("eligible_only", "false").lower() == "true"

    applied_drive_ids = {a.drive_id for a in student.applications}
    results = []
    for d in items:
        if search and search not in d["job_title"].lower() and search not in d["company_name"].lower():
            continue
        drive_obj = PlacementDrive.query.get(d["id"])
        eligible, reason = drive_obj.is_eligible(student) if drive_obj else (False, "Drive unavailable")
        if eligible_only and not eligible:
            continue
        entry = dict(d)
        entry["eligible"] = eligible
        entry["ineligible_reason"] = None if eligible else reason
        entry["already_applied"] = d["id"] in applied_drive_ids
        results.append(entry)
    return {"items": results}, 200


@student_bp.route("/drives/<int:drive_id>", methods=["GET"])
@role_required("student")
def drive_detail(drive_id):
    student, err = _require_student()
    if err:
        return err
    drive = PlacementDrive.query.get_or_404(drive_id)
    eligible, reason = drive.is_eligible(student)
    already_applied = Application.query.filter_by(student_id=student.id, drive_id=drive.id).first() is not None
    data = drive.to_dict()
    data["eligible"] = eligible
    data["ineligible_reason"] = None if eligible else reason
    data["already_applied"] = already_applied
    return {"drive": data}, 200


@student_bp.route("/drives/<int:drive_id>/apply", methods=["POST"])
@role_required("student")
def apply_to_drive(drive_id):
    student, err = _require_student()
    if err:
        return err
    drive = PlacementDrive.query.get_or_404(drive_id)

    if Application.query.filter_by(student_id=student.id, drive_id=drive.id).first():
        return {"message": "You have already applied to this drive."}, 409

    eligible, reason = drive.is_eligible(student)
    if not eligible:
        return {"message": reason}, 400

    application = Application(
        student_id=student.id, drive_id=drive.id, status=ApplicationStatus.APPLIED,
        resume_snapshot_path=student.resume_path,
    )
    db.session.add(application)
    db.session.commit()
    _notify(drive.company.user_id, "New application received",
            f"{student.full_name} applied to '{drive.job_title}'.", "new_application")
    db.session.commit()
    cache.delete("admin_dashboard_stats")
    return {"message": "Application submitted.", "application": application.to_dict()}, 201


@student_bp.route("/applications", methods=["GET"])
@role_required("student")
def my_applications():
    student, err = _require_student()
    if err:
        return err
    apps = Application.query.filter_by(student_id=student.id).order_by(Application.applied_at.desc()).all()
    return {"items": [a.to_dict(include_drive=True) for a in apps]}, 200


@student_bp.route("/applications/<int:application_id>", methods=["GET"])
@role_required("student")
def application_detail(application_id):
    student, err = _require_student()
    if err:
        return err
    application = Application.query.filter_by(id=application_id, student_id=student.id).first()
    if not application:
        return {"message": "Application not found."}, 404
    data = application.to_dict(include_drive=True)
    data["interviews"] = [i.to_dict() for i in application.interviews]
    return {"application": data}, 200


@student_bp.route("/reports", methods=["GET"])
@role_required("student")
def reports():
    student, err = _require_student()
    if err:
        return err
    from application.report_utils import bucket_by_month

    monthly_applications = bucket_by_month([a.applied_at for a in student.applications])
    status_breakdown = {}
    for a in student.applications:
        key = a.status.value if a.status else "unknown"
        status_breakdown[key] = status_breakdown.get(key, 0) + 1

    return {
        "monthly_applications": monthly_applications,
        "status_breakdown": status_breakdown,
    }, 200


@student_bp.route("/export-csv", methods=["POST"])
@role_required("student")
def export_csv():
    student, err = _require_student()
    if err:
        return err
    from application.tasks_export import generate_application_csv
    task = generate_application_csv.delay(student.id)
    return {"message": "Export started. You'll be notified when it's ready.", "task_id": task.id}, 202


@student_bp.route("/export-status/<task_id>", methods=["GET"])
@role_required("student")
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
