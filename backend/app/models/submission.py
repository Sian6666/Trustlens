from datetime import datetime, timezone

from app.extensions import db


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    normalized_content = db.Column(db.Text, nullable=False, index=True)
    source = db.Column(db.String(40), nullable=False, default="message")
    category = db.Column(db.String(40), nullable=False, default="general", index=True)
    risk_score = db.Column(db.Integer, nullable=False, index=True)
    risk_level = db.Column(db.String(20), nullable=False)
    suspicious_phrases = db.Column(db.JSON, nullable=False, default=list)
    detector_reasons = db.Column(db.JSON, nullable=False, default=list)
    scam_votes = db.Column(db.Integer, nullable=False, default=0)
    safe_votes = db.Column(db.Integer, nullable=False, default=0)
    upvotes = db.Column(db.Integer, nullable=False, default=0)
    downvotes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc), index=True)

    user = db.relationship("User", back_populates="submissions")
    votes = db.relationship("Vote", back_populates="submission", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "source": self.source,
            "category": self.category,
            "risk_score": self.risk_score,
            "risk_level": self.risk_level,
            "suspicious_phrases": self.suspicious_phrases,
            "detector_reasons": self.detector_reasons,
            "scam_votes": self.scam_votes,
            "safe_votes": self.safe_votes,
            "upvotes": self.upvotes,
            "downvotes": self.downvotes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
