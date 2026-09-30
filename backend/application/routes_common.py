# backend/application/routes_common.py
import os
from flask import Blueprint, request, current_app as app, send_from_directory
from flask_security import current_user

from application.models import db, CompanyProfile, PlacementDrive, DriveStatus, ApprovalStatus, Notification, Application
from application.auth_utils import any_authenticated, role_required

common_bp = Blueprint("common_bp", __name__, url_prefix="/api")


@common_bp.route("/companies", methods=["GET"])
@any_authenticated
def list_companies():
    companies = CompanyProfile.query.filter_by(approval_status=ApprovalStatus.APPROVED).order_by(CompanyProfile.company_name).all()
    items = []
    for c in companies:
        open_drives = len([d for d in c.drives if d.status == DriveStatus.APPROVED])
        items.append({**c.to_dict(), "open_drive_count": open_drives})
    return {"items": items}, 200


@common_bp.route("/companies/<int:company_id>", methods=["GET"])
@any_authenticated
def public_company(company_id):
    company = CompanyProfile.query.get_or_404(company_id)
    drives = PlacementDrive.query.filter_by(company_id=company.id, status=DriveStatus.APPROVED).all()
    return {"company": company.to_dict(), "drives": [d.to_dict() for d in drives]}, 200


@common_bp.route("/search", methods=["GET"])
@any_authenticated
def search():
    query = request.args.get("q", "").strip()
    if not query:
        return {"companies": [], "drives": []}, 200
    like = f"%{query}%"
    companies = CompanyProfile.query.filter(
        CompanyProfile.company_name.ilike(like), CompanyProfile.approval_status == "approved"
    ).limit(10).all()
    drives = PlacementDrive.query.filter(
        PlacementDrive.job_title.ilike(like), PlacementDrive.status == DriveStatus.APPROVED
    ).limit(10).all()
    return {
        "companies": [c.to_dict() for c in companies],
        "drives": [d.to_dict() for d in drives],
    }, 200


@common_bp.route("/notifications", methods=["GET"])
@any_authenticated
def list_notifications():
    items = Notification.query.filter_by(user_id=current_user.id) \
        .order_by(Notification.created_at.desc()).limit(50).all()
    unread = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
    return {"items": [n.to_dict() for n in items], "unread_count": unread}, 200


@common_bp.route("/notifications/<int:notification_id>/read", methods=["POST"])
@any_authenticated
def mark_notification_read(notification_id):
    n = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first()
    if not n:
        return {"message": "Notification not found."}, 404
    n.is_read = True
    db.session.commit()
    return {"message": "Marked as read."}, 200


@common_bp.route("/notifications/read-all", methods=["POST"])
@any_authenticated
def mark_all_notifications_read():
    Notification.query.filter_by(user_id=current_user.id, is_read=False).update({"is_read": True})
    db.session.commit()
    return {"message": "All notifications marked as read."}, 200


@common_bp.route("/exports/<path:filename>", methods=["GET"])
@any_authenticated
def download_export(filename):
    export_root = os.path.join(app.static_folder, "exports")

    # Exports are per-user (a student's own applications, a company's own
    # drives). Anyone authenticated could otherwise guess/enumerate another
    # user's export filename and download it. A Notification pointing at this
    # exact link is only ever created for the user the export belongs to, so
    # its existence for the current user doubles as an ownership check.
    link = f"/api/exports/{filename}"
    owns_file = Notification.query.filter_by(user_id=current_user.id, link=link).first() is not None
    if not owns_file:
        return {"message": "File not found."}, 404

    return send_from_directory(export_root, filename, as_attachment=True)
