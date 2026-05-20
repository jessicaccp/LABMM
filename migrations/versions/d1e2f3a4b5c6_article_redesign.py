"""article_redesign

Revision ID: d1e2f3a4b5c6
Revises: c1d2e3f4a5b6
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'd1e2f3a4b5c6'
down_revision = 'c1d2e3f4a5b6'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to articles
    with op.batch_alter_table('articles') as batch_op:
        batch_op.add_column(sa.Column('conference', sa.String(256), nullable=True))
        batch_op.add_column(sa.Column(
            'status',
            sa.Enum(
                'in_progress', 'under_review', 'submitted',
                'accepted', 'rejected', 'withdrawn', 'published',
                name='articlestatus'
            ),
            nullable=False,
            server_default='in_progress'
        ))
        batch_op.add_column(sa.Column('submission_deadline', sa.Date(), nullable=True))
        batch_op.add_column(sa.Column('created_at', sa.DateTime(), nullable=True))
        batch_op.drop_column('journal')

    # Create article_in_charge association table
    op.create_table(
        'article_in_charge',
        sa.Column('member_id', sa.Integer(), sa.ForeignKey('members.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('article_id', sa.Integer(), sa.ForeignKey('articles.id', ondelete='CASCADE'), primary_key=True),
    )


def downgrade():
    op.drop_table('article_in_charge')

    with op.batch_alter_table('articles') as batch_op:
        batch_op.drop_column('created_at')
        batch_op.drop_column('submission_deadline')
        batch_op.drop_column('status')
        batch_op.drop_column('conference')
        batch_op.add_column(sa.Column('journal', sa.String(128), nullable=True))
