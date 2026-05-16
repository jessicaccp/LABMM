import enum
from datetime import datetime, timezone

from labmm.extensions import db


class LabRole(str, enum.Enum):
    ceo = "ceo"                               # Professor responsible for the lab
    engineering_manager = "engineering_manager"
    project_manager = "project_manager"
    research_manager = "research_manager"
    tech_lead = "tech_lead"
    engineer = "engineer"
    researcher = "researcher"
    staff = "staff"


# Roles that can manage lab membership
MANAGER_ROLES = frozenset({
    LabRole.ceo,
    LabRole.engineering_manager,
    LabRole.project_manager,
    LabRole.research_manager,
})


class CompensationType(str, enum.Enum):
    project_salary = "project_salary"
    research_grant = "research_grant"


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
    compensation_type = db.Column(db.Enum(CompensationType), nullable=True)
    compensation_value = db.Column(db.Numeric(10, 2), nullable=True)

    # Relationships
    member = db.relationship("Member", back_populates="lab_memberships")
    laboratory = db.relationship("Laboratory", back_populates="memberships")

    def __repr__(self) -> str:
        return f"<LabMembership member={self.member_id} lab={self.lab_id} role={self.role}>"
