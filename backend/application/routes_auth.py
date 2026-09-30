# backend/application/routes_auth.py
from datetime import datetime
from flask import Blueprint, current_app as app, request, jsonify
from flask_security import verify_password, hash_password, auth_required, current_user

from application.models import db, User, StudentProfile, CompanyProfile, ApprovalStatus, PortalVisit
from application.auth_utils import any_authenticated, validate_password_strength as _validate_password

auth_bp = Blueprint("auth_bp", __name__)


def _user_public(user: User):
    data = {
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "active": user.active,
        "roles": [r.name for r in user.roles],
        "role": user.role_name(),
        "created_at": user.created_at.strftime("%Y-%m-%d") if user.created_at else None,
    }
    if user.student_profile:
        data["profile"] = user.student_profile.to_dict()
    elif user.company_profile:
        data["profile"] = user.company_profile.to_dict()
    return data


@auth_bp.route("/")
def home():
    return {"message": "Placement Portal API is running"}, 200


@auth_bp.route("/register/student", methods=["POST"])
def register_student():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    full_name = (data.get("full_name") or "").strip()
    branch = (data.get("branch") or "").strip()
    year = data.get("year")
    cgpa = data.get("cgpa")
    phone = (data.get("phone") or "").strip()

    if not all([username, email, password, confirm_password, full_name, branch, year]):
        return {"message": "Please fill all required fields."}, 400
    if password != confirm_password:
        return {"message": "Passwords do not match."}, 400
    err = _validate_password(password)
    if err:
        return {"message": err}, 400
    try:
        year = int(year)
        cgpa = float(cgpa) if cgpa not in (None, "") else 0.0
    except (TypeError, ValueError):
        return {"message": "Year must be an integer and CGPA a number."}, 400
    if cgpa < 0 or cgpa > 10:
        return {"message": "CGPA must be between 0 and 10."}, 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return {"message": "Email or username is already registered."}, 409

    datastore = app.security.datastore
    user = datastore.create_user(
        username=username, email=email, password=hash_password(password),
        fs_uniquifier=f"fs-student-{email}", roles=["student"],
    )
    db.session.commit()
    db.session.add(StudentProfile(
        user_id=user.id, full_name=full_name, branch=branch, year=year,
        cgpa=cgpa, phone=phone,
    ))
    db.session.commit()
    return {"message": "Registration successful. You can now log in."}, 201


@auth_bp.route("/register/company", methods=["POST"])
def register_company():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""
    company_name = (data.get("company_name") or "").strip()
    hr_contact_name = (data.get("hr_contact_name") or "").strip()
    hr_email = (data.get("hr_email") or email).strip().lower()
    hr_phone = (data.get("hr_phone") or "").strip()
    website = (data.get("website") or "").strip()
    description = (data.get("description") or "").strip()
    industry = (data.get("industry") or "").strip()

    if not all([username, email, password, confirm_password, company_name]):
        return {"message": "Please fill all required fields."}, 400
    if password != confirm_password:
        return {"message": "Passwords do not match."}, 400
    err = _validate_password(password)
    if err:
        return {"message": err}, 400

    if User.query.filter((User.email == email) | (User.username == username)).first():
        return {"message": "Email or username is already registered."}, 409

    datastore = app.security.datastore
    user = datastore.create_user(
        username=username, email=email, password=hash_password(password),
        fs_uniquifier=f"fs-company-{email}", roles=["company"],
    )
    db.session.commit()
    db.session.add(CompanyProfile(
        user_id=user.id, company_name=company_name, hr_contact_name=hr_contact_name,
        hr_email=hr_email, hr_phone=hr_phone, website=website, description=description,
        industry=industry, approval_status=ApprovalStatus.PENDING,
    ))
    db.session.commit()
    return {"message": "Registration submitted. An admin needs to approve your company before you can post drives."}, 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not email or not password:
        return {"message": "Email and password are required."}, 400

    datastore = app.security.datastore
    user = datastore.find_user(email=email)
    if not user or not verify_password(password, user.password):
        return {"message": "Invalid email or password."}, 401
    if not user.active:
        return {"message": "Your account has been deactivated by the admin."}, 403

    db.session.add(PortalVisit(user_id=user.id, role=user.role_name() or "unknown"))
    db.session.commit()

    token = user.get_auth_token()
    return {"token": token, "user": _user_public(user)}, 200


@auth_bp.route("/logout", methods=["POST"])
@auth_required("token")
def logout():
    return {"message": "Logged out. Please discard the token on the client."}, 200


@auth_bp.route("/user", methods=["GET"])
@any_authenticated
def get_current_user():
    return {"user": _user_public(current_user)}, 200
