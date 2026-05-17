"""add_member_approval

Revision ID: e6b77a9e0728
Revises: a1b2c3d4e5f6
Create Date: 2026-05-16 21:29:59.942174

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e6b77a9e0728'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_approved', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('desired_lab_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_members_desired_lab', 'laboratories', ['desired_lab_id'], ['id'], ondelete='SET NULL')

    # Grandfather all existing members as approved
    op.execute("UPDATE members SET is_approved = 1")


def downgrade():
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_constraint('fk_members_desired_lab', type_='foreignkey')
        batch_op.drop_column('desired_lab_id')
        batch_op.drop_column('is_approved')
