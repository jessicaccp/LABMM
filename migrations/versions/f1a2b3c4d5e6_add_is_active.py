"""add_is_active

Revision ID: f1a2b3c4d5e6
Revises: e6b77a9e0728
Create Date: 2026-05-17

"""
from alembic import op
import sqlalchemy as sa

revision = 'f1a2b3c4d5e6'
down_revision = 'e6b77a9e0728'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('members') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))

    with op.batch_alter_table('laboratories') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))

    with op.batch_alter_table('projects') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))

    with op.batch_alter_table('research_groups') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))

    with op.batch_alter_table('articles') as batch_op:
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))


def downgrade():
    with op.batch_alter_table('articles') as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('research_groups') as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('projects') as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('laboratories') as batch_op:
        batch_op.drop_column('is_active')

    with op.batch_alter_table('members') as batch_op:
        batch_op.drop_column('is_active')
