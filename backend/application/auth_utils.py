# backend/application/auth_utils.py
import re
from functools import wraps
from flask import jsonify, request
from flask_security import auth_required, current_user


def validate_password_strength(pw: str):
    """Shared password rule, used at registration and whenever an admin resets
    a student/company account's password from the admin profile-edit screen."""
    if not pw or len(pw) < 6:
        return "Password must be at least 6 characters long."
    if not re.search(r"[A-Za-z]", pw):
        return "Password must include at least one letter."
    if not re.search(r"[0-9]", pw):
        return "Password must include at least one number."
    return None


def role_required(*roles):
    """Require a valid Authentication-Token AND that the user has one of `roles`.
    Also blocks accounts the admin has deactivated."""
    def decorator(fn):
        @wraps(fn)
        @auth_required("token")
        def wrapper(*args, **kwargs):
            if not current_user.active:
                return jsonify({"message": "Your account has been deactivated by the admin."}), 403
            if roles and not any(current_user.has_role(r) for r in roles):
                return jsonify({"message": "You don't have access to this resource."}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def any_authenticated(fn):
    @wraps(fn)
    @auth_required("token")
    def wrapper(*args, **kwargs):
        if not current_user.active:
            return jsonify({"message": "Your account has been deactivated by the admin."}), 403
        return fn(*args, **kwargs)
    return wrapper


def paginate_args():
    try:
        page = max(int(request.args.get("page", 1)), 1)
        per_page = min(max(int(request.args.get("per_page", 20)), 1), 100)
    except (TypeError, ValueError):
        page, per_page = 1, 20
    return page, per_page
