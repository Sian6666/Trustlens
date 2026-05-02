from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import func

from app.extensions import db
from app.models import Submission
from app.services.cache import get_json, set_json
from app.utils.validation import parse_category

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.get("/trending")
def trending():
    category = request.args.get("category")
    cache_key = f"dashboard:trending:{category or 'all'}"
    cached = get_json(cache_key)
    if cached:
        return jsonify(cached)

    query = Submission.query
    if category:
        query = query.filter(Submission.category == parse_category(category))

    items = (
        query.order_by(
            (Submission.scam_votes + Submission.upvotes - Submission.downvotes).desc(),
            Submission.risk_score.desc(),
            Submission.created_at.desc(),
        )
        .limit(12)
        .all()
    )
    response = {"items": [item.to_dict() for item in items]}
    set_json(cache_key, response, ttl=45)
    return jsonify(response)


@dashboard_bp.get("/risk-trends")
def risk_trends():
    cache_key = "dashboard:risk-trends"
    cached = get_json(cache_key)
    if cached:
        return jsonify(cached)

    since = datetime.now(timezone.utc) - timedelta(days=14)
    rows = (
        db.session.query(
            func.date(Submission.created_at).label("day"),
            func.avg(Submission.risk_score).label("average_risk"),
            func.count(Submission.id).label("count"),
        )
        .filter(Submission.created_at >= since)
        .group_by(func.date(Submission.created_at))
        .order_by(func.date(Submission.created_at))
        .all()
    )

    response = {
        "items": [
            {
                "day": str(row.day),
                "average_risk": round(float(row.average_risk or 0), 2),
                "count": int(row.count),
            }
            for row in rows
        ]
    }
    set_json(cache_key, response, ttl=60)
    return jsonify(response)
