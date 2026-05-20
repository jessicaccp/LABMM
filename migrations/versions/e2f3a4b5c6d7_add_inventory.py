"""add_inventory

Revision ID: e2f3a4b5c6d7
Revises: d1e2f3a4b5c6
Create Date: 2026-05-20

"""
from alembic import op
import sqlalchemy as sa

revision = 'e2f3a4b5c6d7'
down_revision = 'd1e2f3a4b5c6'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'inventory_items',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(128), nullable=False),
        sa.Column('category', sa.String(64), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('serial_number', sa.String(128), nullable=True),
        sa.Column('quantity', sa.Integer(), nullable=False, server_default='1'),
        sa.Column(
            'condition',
            sa.Enum('new', 'good', 'fair', 'poor', 'broken', name='itemcondition'),
            nullable=False,
            server_default='good'
        ),
        sa.Column('lab_id', sa.Integer(), sa.ForeignKey('laboratories.id', ondelete='CASCADE'), nullable=False),
        sa.Column('assigned_to_id', sa.Integer(), sa.ForeignKey('members.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
    )
    op.create_index('ix_inventory_items_lab_id', 'inventory_items', ['lab_id'])


def downgrade():
    op.drop_index('ix_inventory_items_lab_id', table_name='inventory_items')
    op.drop_table('inventory_items')
