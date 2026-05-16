import enum
from datetime import datetime, timezone

from labmm.extensions import db


class LabRole(str, enum.Enum):
    manager = "manager"
    engineer = "engineer"
    researcher = "researcher"
    staff = "staff"


class LabMembership(db.Model):
    __tablename__ = "lab_memberships"

    member_id = db.Column(
        db.Integer, db.ForeignKey("members.id", ondelete="CASCADE"), primary_key=True
    )
    lab_id = db.Column(
        db.Integer,
        db.ForeignKey("laboratories.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role = db.Column(db.Enum(LabRole), nullable=False)
    joined_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )

    # Relationships
    member = db.relationship("Member", back_populates="lab_memberships")
    laboratory = db.relationship("Laboratory", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<LabMembership member={self.member_id} lab={self.lab_id} role={self.role}>"
