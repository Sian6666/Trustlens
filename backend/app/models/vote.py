from datetime import datetime, timezone

from app.extensions import db


class Vote(db.Model):
    __tablename__ = "votes"
    __table_args__ = (
        db.UniqueConstraint("user_id", "submission_id", "vote_type", name="uq_vote_once"),
    )

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    submission_id = db.Column(
        db.Integer, db.ForeignKey("submissions.id"), nullable=False, index=True
    )
    vote_type = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship("User", back_populates="votes")
    submission = db.relationship("Submission", back_populates="votes")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "submission_id": self.submission_id,
            "vote_type": self.vote_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
