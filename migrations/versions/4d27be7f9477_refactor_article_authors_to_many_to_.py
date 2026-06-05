"""refactor article authors to many-to-many relationship

Revision ID: 4d27be7f9477
Revises: g4b5c6d7e8f9
Create Date: 2026-06-05 14:30:14.427251

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = '4d27be7f9477'
down_revision = 'g4b5c6d7e8f9'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('article_authors',
    sa.Column('member_id', sa.Integer(), nullable=False),
    sa.Column('article_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['article_id'], ['articles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['member_id'], ['members.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('member_id', 'article_id')
    )
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.alter_column('created_at',
               existing_type=sa.DATETIME(),
               nullable=False)
        batch_op.drop_column('authors')


def downgrade():
    with op.batch_alter_table('articles', schema=None) as batch_op:
        batch_op.add_column(sa.Column('authors', sqlite.JSON(), server_default=sa.text("'[]'"), nullable=False))
        batch_op.alter_column('created_at',
               existing_type=sa.DATETIME(),
               nullable=True)

    op.drop_table('article_authors')
