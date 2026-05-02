from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.extensions import db, limiter, socketio
from app.models import Submission, Vote
from app.services.cache import invalidate_prefix
from app.services.detector import analyze_content
from app.utils.validation import (
    ALLOWED_VOTES,
    normalize_for_search,
    parse_category,
    parse_source,
    sanitize_text,
)

submissions_bp = Blueprint("submissions", __name__)


@submissions_bp.post("")
@jwt_required()
@limiter.limit("30 per minute")
def create_submission():
    payload = request.get_json(silent=True) or {}
    content = sanitize_text(payload.get("content", ""))
    category = parse_category(payload.get("category"))
    source = parse_source(payload.get("source"))
    analysis = analyze_content(content)

    submission = Submission(
        user_id=int(get_jwt_identity()),
        content=content,
        normalized_content=normalize_for_search(content),
        category=category,
        source=source,
        **analysis,
    )
    db.session.add(submission)
    db.session.commit()

    invalidate_prefix("dashboard:")
    socketio.emit("submission:new", submission.to_dict())
    return jsonify({"submission": submission.to_dict()}), 201


@submissions_bp.get("")
@jwt_required()
def list_submissions():
    page, per_page = pagination_args()
    category = request.args.get("category")
    min_risk = request.args.get("min_risk", type=int)

    query = Submission.query.order_by(Submission.created_at.desc())
    if category:
        query = query.filter(Submission.category == parse_category(category))
    if min_risk is not None:
        query = query.filter(Submission.risk_score >= max(0, min(100, min_risk)))

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(paginated_response(pagination))


@submissions_bp.get("/search")
@jwt_required()
def search_submissions():
    query_text = normalize_for_search(request.args.get("q", ""))
    if len(query_text) < 2:
        return jsonify({"items": [], "page": 1, "pages": 0, "total": 0})

    page, per_page = pagination_args()
    like_query = f"%{query_text}%"
    query = (
        Submission.query.filter(
            or_(
                Submission.normalized_content.ilike(like_query),
                Submission.category.ilike(like_query),
            )
        )
        .order_by(Submission.risk_score.desc(), Submission.created_at.desc())
    )
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify(paginated_response(pagination))


@submissions_bp.get("/<int:submission_id>")
@jwt_required()
def get_submission(submission_id):
    submission = db.get_or_404(Submission, submission_id)
    return jsonify({"submission": submission.to_dict()})


@submissions_bp.post("/<int:submission_id>/votes")
@jwt_required()
@limiter.limit("60 per minute")
def vote_submission(submission_id):
    submission = db.get_or_404(Submission, submission_id)
    payload = request.get_json(silent=True) or {}
    vote_type = (payload.get("vote_type") or "").lower().strip()
    if vote_type not in ALLOWED_VOTES:
        return jsonify({"error": "invalid_vote", "message": "Unsupported vote type"}), 400

    vote = Vote(
        user_id=int(get_jwt_identity()),
        submission_id=submission.id,
        vote_type=vote_type,
    )
    db.session.add(vote)
    try:
        increment_vote(submission, vote_type)
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({"error": "duplicate_vote", "message": "Vote already recorded"}), 409

    invalidate_prefix("dashboard:")
    socketio.emit("vote:new", {"submission": submission.to_dict(), "vote": vote.to_dict()})
    return jsonify({"submission": submission.to_dict(), "vote": vote.to_dict()}), 201


def increment_vote(submission, vote_type):
    if vote_type == "scam":
        submission.scam_votes += 1
    elif vote_type == "safe":
        submission.safe_votes += 1
    elif vote_type == "upvote":
        submission.upvotes += 1
    elif vote_type == "downvote":
        submission.downvotes += 1


def pagination_args():
    page = max(1, request.args.get("page", default=1, type=int))
    per_page = min(50, max(1, request.args.get("per_page", default=10, type=int)))
    return page, per_page


def paginated_response(pagination):
    return {
        "items": [item.to_dict() for item in pagination.items],
        "page": pagination.page,
        "pages": pagination.pages,
        "per_page": pagination.per_page,
        "total": pagination.total,
    }
