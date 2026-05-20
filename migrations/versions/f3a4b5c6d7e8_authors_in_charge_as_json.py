"""authors_in_charge_as_json

Revision ID: f3a4b5c6d7e8
Revises: e2f3a4b5c6d7
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'f3a4b5c6d7e8'
down_revision = 'e2f3a4b5c6d7'
branch_labels = None
depends_on = None


def upgrade():
    # Drop the M2M association tables
    op.drop_table('article_in_charge')
    op.drop_table('article_authors')

    # Add JSON columns for free-text authors and in_charge lists
    with op.batch_alter_table('articles') as batch_op:
        batch_op.add_column(
            sa.Column('authors', sa.JSON(), nullable=False, server_default='[]')
        )
        batch_op.add_column(
            sa.Column('in_charge', sa.JSON(), nullable=False, server_default='[]')
        )


def downgrade():
    with op.batch_alter_table('articles') as batch_op:
        batch_op.drop_column('in_charge')
        batch_op.drop_column('authors')

    op.create_table(
        'article_authors',
        sa.Column('member_id', sa.Integer(), sa.ForeignKey('members.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    )
    op.create_table(
        'article_in_charge',
        sa.Column('member_id', sa.Integer(), sa.ForeignKey('members.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    )
