"""add reports_to_id to lab_memberships

Revision ID: b3c4d5e6f7a8
Revises: a2b3c4d5e6f7
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'b3c4d5e6f7a8'
down_revision = 'a2b3c4d5e6f7'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.add_column(sa.Column('reports_to_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            'fk_memberships_reports_to_id',
            'members',
            ['reports_to_id'],
            ['id'],
        )


def downgrade():
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.drop_constraint('fk_memberships_reports_to_id', type_='foreignkey')
        batch_op.drop_column('reports_to_id')
