# backend/application/routes_common.py
import os
import time
import re
from collections import defaultdict
from flask import Blueprint, request, current_app as app, send_from_directory
from flask_security import current_user
from email_validator import validate_email, EmailNotValidError

from application.models import db, User, CompanyProfile, PlacementDrive, DriveStatus, ApprovalStatus, Notification, Application
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


# ---------------------------------------------------------------- contact form
# In-memory per-IP cooldown (process-local; resets on restart). A college-project
# scale deployment doesn't warrant pulling in Redis-backed rate limiting just for
# this one public, unauthenticated endpoint — but it's the one endpoint in the
# whole app that accepts input from someone who isn't logged in at all, so it
# needs *some* abuse guard rather than none.
_contact_attempts = defaultdict(list)
_CONTACT_MAX_PER_WINDOW = 5
_CONTACT_WINDOW_SECONDS = 15 * 60


def _contact_rate_limited(ip):
    now = time.time()
    attempts = [t for t in _contact_attempts[ip] if now - t < _CONTACT_WINDOW_SECONDS]
    _contact_attempts[ip] = attempts
    if len(attempts) >= _CONTACT_MAX_PER_WINDOW:
        return True
    attempts.append(now)
    return False


@common_bp.route("/contact", methods=["POST"])
def submit_contact():
    """Public contact form — intentionally has no @any_authenticated /
    @role_required decorator, since a visitor who hasn't registered yet is
    exactly who this is for. Every other endpoint in the app requires a valid
    Authentication-Token; this is the one deliberate exception, so it gets its
    own validation, length limits and rate limiting instead of relying on auth
    to keep abuse out."""
    # Deliberately NOT trusting X-Forwarded-For here: this app isn't run behind
    # a reverse proxy, so that header is fully attacker-controlled input and
    # trusting it would make the rate limit trivially bypassable (send a
    # different fake value each request). If this is ever deployed behind
    # Nginx/a load balancer, switch to Werkzeug's ProxyFix middleware in
    # app.py rather than reading the header directly here.
    ip = request.remote_addr or "unknown"
    if _contact_rate_limited(ip):
        return {"message": "Too many messages sent recently. Please try again later."}, 429

    data = request.get_json(silent=True) or {}

    # Honeypot: a hidden field real users never see or fill. Bots that
    # autofill every field will populate it — report success without
    # actually sending anything, so the bot has no signal to adapt to.
    if (data.get("company_website") or "").strip():
        return {"message": "Thanks — your message has been sent."}, 200

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    subject = (data.get("subject") or "General enquiry").strip()
    message = (data.get("message") or "").strip()

    if not (2 <= len(name) <= 100):
        return {"message": "Please enter your name (2-100 characters)."}, 400
    if not (10 <= len(message) <= 2000):
        return {"message": "Message must be between 10 and 2000 characters."}, 400
    if len(subject) > 150:
        return {"message": "Subject is too long."}, 400
    # Strip any stray control characters from free-text fields before they're
    # ever written into an email body.
    name = re.sub(r"[\r\n\t]+", " ", name)
    subject = re.sub(r"[\r\n\t]+", " ", subject)

    try:
        valid = validate_email(email, check_deliverability=False)
        email = valid.normalized
    except EmailNotValidError:
        return {"message": "Please enter a valid email address."}, 400

    from application.mail_helper import send_email
    admin_user = User.query.join(User.roles).filter_by(name="admin").first()
    recipient = admin_user.email if admin_user else app.config.get("SENDER_ADDRESS")

    sent = send_email(
        recipient,
        f"[Contact form] {subject}",
        f"New message from the Placement Portal contact page.\n\n"
        f"Name: {name}\nEmail: {email}\nSubject: {subject}\n\nMessage:\n{message}\n",
    )
    if not sent:
        db.session.add(Notification(
            user_id=admin_user.id, title="New contact form message", type="system",
            message=f"{name} ({email}): {subject}",
        )) if admin_user else None
        db.session.commit()

    return {"message": "Thanks — your message has been sent. We'll get back to you soon."}, 200


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
