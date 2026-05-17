"""add dynamic roles table

Revision ID: a2b3c4d5e6f7
Revises: 2d2babd5edd6
Create Date: 2026-05-17 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = 'a2b3c4d5e6f7'
down_revision = '2d2babd5edd6'
branch_labels = None
depends_on = None

_SYSTEM_ROLES = [
    {'key': 'ceo',                  'name': 'CEO',                  'level': 0, 'is_system': True},
    {'key': 'engineering_manager',  'name': 'Engineering Manager',  'level': 1, 'is_system': True},
    {'key': 'project_manager',      'name': 'Project Manager',      'level': 1, 'is_system': True},
    {'key': 'chief_scientist',      'name': 'Chief Scientist',      'level': 1, 'is_system': True},
    {'key': 'tech_lead',            'name': 'Tech Lead',            'level': 2, 'is_system': True},
    {'key': 'engineer',             'name': 'Engineer',             'level': 3, 'is_system': True},
    {'key': 'researcher',           'name': 'Researcher',           'level': 3, 'is_system': True},
    {'key': 'research_fellow',      'name': 'Research Fellow',      'level': 3, 'is_system': True},
    {'key': 'staff',                'name': 'Staff',                'level': 4, 'is_system': True},
]

_roles_table = sa.table(
    'roles',
    sa.column('key', sa.String),
    sa.column('name', sa.String),
    sa.column('level', sa.Integer),
    sa.column('is_system', sa.Boolean),
)


def upgrade():
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(64), nullable=False),
        sa.Column('name', sa.String(64), nullable=False),
        sa.Column('level', sa.Integer(), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key'),
    )

    op.bulk_insert(_roles_table, _SYSTEM_ROLES)

    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.alter_column(
            'role',
            existing_type=sa.Enum(
                'ceo', 'engineering_manager', 'project_manager', 'chief_scientist',
                'tech_lead', 'engineer', 'researcher', 'research_fellow', 'staff',
                name='labrole',
            ),
            type_=sa.String(64),
            existing_nullable=False,
        )


def downgrade():
    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.alter_column(
            'role',
            existing_type=sa.String(64),
            type_=sa.Enum(
                'ceo', 'engineering_manager', 'project_manager', 'chief_scientist',
                'tech_lead', 'engineer', 'researcher', 'research_fellow', 'staff',
                name='labrole',
            ),
            existing_nullable=False,
        )

    op.drop_table('roles')
