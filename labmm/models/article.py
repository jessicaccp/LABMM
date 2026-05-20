import enum
from datetime import datetime, timezone

from labmm.extensions import db


class ArticleStatus(str, enum.Enum):
    in_progress = "in_progress"
    under_review = "under_review"
    submitted = "submitted"
    accepted = "accepted"
    rejected = "rejected"
    withdrawn = "withdrawn"
    published = "published"


class Article(db.Model):
    __tablename__ = "articles"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False)
    abstract = db.Column(db.Text, nullable=True)
    conference = db.Column(db.String(256), nullable=True)
    doi = db.Column(db.String(128), unique=True, nullable=True)
    status = db.Column(
        db.Enum(ArticleStatus), default=ArticleStatus.in_progress, nullable=False
    )
    submission_deadline = db.Column(db.Date, nullable=True)
    published_at = db.Column(db.Date, nullable=True)
    authors = db.Column(db.JSON, nullable=False, default=list)       # list of free-text names
    in_charge = db.Column(db.JSON, nullable=False, default=list)     # list of free-text names
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    lab_id = db.Column(
        db.Integer,
        db.ForeignKey("laboratories.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    laboratory = db.relationship("Laboratory", back_populates="articles")

    def __repr__(self) -> str:
        return f"<Article {self.title}>"
