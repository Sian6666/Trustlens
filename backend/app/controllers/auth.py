from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required

from app.extensions import db, limiter
from app.models import User
from app.utils.validation import sanitize_text, validate_email_address, validate_password

auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/signup")
@limiter.limit("8 per minute")
def signup():
    payload = request.get_json(silent=True) or {}
    name = sanitize_text(payload.get("name", ""), max_length=120)
    email = validate_email_address(payload.get("email", ""))
    password = validate_password(payload.get("password", ""))

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "email_exists", "message": "Email is already registered"}), 409

    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()}), 201


@auth_bp.post("/login")
@limiter.limit("12 per minute")
def login():
    payload = request.get_json(silent=True) or {}
    email = validate_email_address(payload.get("email", ""))
    password = payload.get("password", "")
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"error": "invalid_credentials", "message": "Invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": token, "user": user.to_dict()})


@auth_bp.get("/me")
@jwt_required()
def me():
    user = db.session.get(User, int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "not_found", "message": "User not found"}), 404
    return jsonify({"user": user.to_dict()})


@auth_bp.post("/logout")
@jwt_required()
def logout():
    return jsonify({"message": "Client should discard the access token"})
