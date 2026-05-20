"""rename_ceo_to_lab_coordinator

Revision ID: g4b5c6d7e8f9
Revises: f3a4b5c6d7e8
Create Date: 2026-05-20

"""
import json

from alembic import op
import sqlalchemy as sa

revision = 'g4b5c6d7e8f9'
down_revision = 'f3a4b5c6d7e8'
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()

    # 1. Rename the system role row in the `roles` table
    bind.execute(
        sa.text(
            "UPDATE roles SET key = 'lab_coordinator', name = 'Lab Coordinator' "
            "WHERE key = 'ceo'"
        )
    )

    # 2. Update every lab_memberships row whose `roles` JSON array contains "ceo"
    rows = bind.execute(
        sa.text("SELECT member_id, lab_id, roles FROM lab_memberships")
    ).fetchall()

    for member_id, lab_id, roles_raw in rows:
        # roles may be stored as a JSON string or already parsed (depends on driver)
        if isinstance(roles_raw, str):
            roles = json.loads(roles_raw)
        else:
            roles = roles_raw  # already a list

        if roles and "ceo" in roles:
            new_roles = ["lab_coordinator" if r == "ceo" else r for r in roles]
            bind.execute(
                sa.text(
                    "UPDATE lab_memberships SET roles = :roles "
                    "WHERE member_id = :mid AND lab_id = :lid"
                ),
                {"roles": json.dumps(new_roles), "mid": member_id, "lid": lab_id},
            )


def downgrade():
    bind = op.get_bind()

    # 1. Revert the system role row
    bind.execute(
        sa.text(
            "UPDATE roles SET key = 'ceo', name = 'CEO' "
            "WHERE key = 'lab_coordinator'"
        )
    )

    # 2. Revert lab_memberships JSON arrays
    rows = bind.execute(
        sa.text("SELECT member_id, lab_id, roles FROM lab_memberships")
    ).fetchall()

    for member_id, lab_id, roles_raw in rows:
        if isinstance(roles_raw, str):
            roles = json.loads(roles_raw)
        else:
            roles = roles_raw

        if roles and "lab_coordinator" in roles:
            new_roles = ["ceo" if r == "lab_coordinator" else r for r in roles]
            bind.execute(
                sa.text(
                    "UPDATE lab_memberships SET roles = :roles "
                    "WHERE member_id = :mid AND lab_id = :lid"
                ),
                {"roles": json.dumps(new_roles), "mid": member_id, "lid": lab_id},
            )
