"""roles as json array

Revision ID: c1d2e3f4a5b6
Revises: b3c4d5e6f7a8
Create Date: 2025-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'c1d2e3f4a5b6'
down_revision = 'b3c4d5e6f7a8'
branch_labels = None
depends_on = None


def upgrade():
    # Step 1: Add roles as nullable JSON column
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.add_column(sa.Column('roles', sa.JSON(), nullable=True))

    # Step 2: Migrate existing role strings into JSON arrays
    op.execute("UPDATE lab_memberships SET roles = json_array(role)")

    # Step 3: Make roles non-nullable and drop old role column
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.alter_column('roles', existing_type=sa.JSON(), nullable=False)
        batch_op.drop_column('role')


def downgrade():
    # Step 1: Add role back as nullable string column
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(64), nullable=True))

    # Step 2: Extract first element of roles array
    op.execute("UPDATE lab_memberships SET role = json_extract(roles, '$[0]')")

    # Step 3: Make role non-nullable and drop roles column
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.alter_column('role', existing_type=sa.String(64), nullable=False)
        batch_op.drop_column('roles')
