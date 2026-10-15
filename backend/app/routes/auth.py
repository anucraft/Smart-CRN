from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from ..extensions import db
from ..models import Admin
from ..utils.responses import error

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


@bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    if not email or not password:
        return error("Email and password are required.", 400)
    admin = Admin.query.filter_by(email=email).first()
    # Same message for unknown email and wrong password: don't reveal which accounts exist.
    if admin is None or not admin.check_password(password):
        return error("Invalid email or password.", 401)
    token = create_access_token(identity=str(admin.id))
    return jsonify({"access_token": token, "admin": admin.to_dict()})


@bp.get("/me")
@jwt_required()
def me():
    admin = db.session.get(Admin, int(get_jwt_identity()))
    if admin is None:
        return error("Account no longer exists.", 401)
    return jsonify({"admin": admin.to_dict()})
