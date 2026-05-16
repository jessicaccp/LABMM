from datetime import datetime, timezone

from werkzeug.security import check_password_hash, generate_password_hash

from labmm.extensions import db


class Member(db.Model):
    __tablename__ = "members"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    is_super_admin = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    lab_memberships = db.relationship(
        "LabMembership", back_populates="member", cascade="all, delete-orphan"
    )
    authored_articles = db.relationship(
        "Article", secondary="article_authors", back_populates="authors"
    )
    research_groups = db.relationship(
        "Research", secondary="member_research", back_populates="members"
    )
    projects = db.relationship(
        "Project", secondary="member_projects", back_populates="members"
    )

    def set_password(self, password: str) -> None:
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def __repr__(self) -> str:
        return f"<Member {self.email}>"
