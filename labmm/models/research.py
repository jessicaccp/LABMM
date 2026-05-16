from datetime import datetime, timezone

from labmm.extensions import db

member_research = db.Table(
    "member_research",
    db.Column(
        "member_id",
        db.Integer,
        db.ForeignKey("members.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    db.Column(
        "research_id",
        db.Integer,
        db.ForeignKey("research_groups.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Research(db.Model):
    __tablename__ = "research_groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text, nullable=True)
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
    laboratory = db.relationship("Laboratory", back_populates="research_groups")
    members = db.relationship(
        "Member", secondary="member_research", back_populates="research_groups"
    )
    projects = db.relationship("Project", back_populates="research_group")

    def __repr__(self) -> str:
        return f"<Research {self.name}>"
