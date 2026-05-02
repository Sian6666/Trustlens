from flask import Blueprint, jsonify
from sqlalchemy import text

from app.extensions import db
from app.services.cache import get_json, set_json

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health():
    return jsonify({"status": "ok", "service": "trustlens-api"})


@health_bp.get("/ready")
def ready():
    checks = {"database": "ok", "cache": "ok"}
    status_code = 200

    try:
        db.session.execute(text("select 1"))
    except Exception:
        checks["database"] = "error"
        status_code = 503

    try:
        set_json("health:ready", {"ok": True}, ttl=5)
        get_json("health:ready")
    except Exception:
        checks["cache"] = "error"
        status_code = 503

    return jsonify({"status": "ok" if status_code == 200 else "degraded", "checks": checks}), status_code
