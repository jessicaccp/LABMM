"""hierarchy: cpf, professor, chief_scientist, research_fellow, volunteer, specialization, manager_id, tech_lead_id

Revision ID: a1b2c3d4e5f6
Revises: 0a98b5af9357
Create Date: 2026-05-16 23:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '0a98b5af9357'
branch_labels = None
depends_on = None


def upgrade():
    # ── members table ────────────────────────────────────────────────────────
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.add_column(sa.Column('cpf', sa.String(11), nullable=True))
        batch_op.add_column(sa.Column('is_professor', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.create_unique_constraint('uq_members_cpf', ['cpf'])
        batch_op.create_index('ix_members_cpf', ['cpf'], unique=True)

    # ── lab_memberships table ────────────────────────────────────────────────
    # Data migration: rename research_manager → chief_scientist before altering enum
    op.execute("UPDATE lab_memberships SET role = 'chief_scientist' WHERE role = 'research_manager'")

    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.alter_column(
            'role',
            existing_type=sa.Enum(
                'ceo', 'engineering_manager', 'project_manager', 'research_manager',
                'tech_lead', 'engineer', 'researcher', 'staff',
                name='labrole',
            ),
            type_=sa.Enum(
                'ceo', 'engineering_manager', 'project_manager', 'chief_scientist',
                'tech_lead', 'engineer', 'researcher', 'research_fellow', 'staff',
                name='labrole',
            ),
            existing_nullable=False,
        )
        batch_op.alter_column(
            'compensation_type',
            existing_type=sa.Enum('project_salary', 'research_grant', name='compensationtype'),
            type_=sa.Enum('project_salary', 'research_grant', 'volunteer', name='compensationtype'),
            existing_nullable=True,
        )
        batch_op.add_column(sa.Column('specialization', sa.String(64), nullable=True))

    # ── research_groups table ────────────────────────────────────────────────
    with op.batch_alter_table('research_groups', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('manager_id', sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            'fk_research_groups_manager_id',
            'members',
            ['manager_id'],
            ['id'],
            ondelete='SET NULL',
        )

    # ── projects table ───────────────────────────────────────────────────────
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.add_column(
            sa.Column('tech_lead_id', sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            'fk_projects_tech_lead_id',
            'members',
            ['tech_lead_id'],
            ['id'],
            ondelete='SET NULL',
        )


def downgrade():
    # ── projects table ───────────────────────────────────────────────────────
    with op.batch_alter_table('projects', schema=None) as batch_op:
        batch_op.drop_constraint('fk_projects_tech_lead_id', type_='foreignkey')
        batch_op.drop_column('tech_lead_id')

    # ── research_groups table ────────────────────────────────────────────────
    with op.batch_alter_table('research_groups', schema=None) as batch_op:
        batch_op.drop_constraint('fk_research_groups_manager_id', type_='foreignkey')
        batch_op.drop_column('manager_id')

    # ── lab_memberships table ────────────────────────────────────────────────
    op.execute("UPDATE lab_memberships SET role = 'research_manager' WHERE role = 'chief_scientist'")

    with op.batch_alter_table('lab_memberships', schema=None) as batch_op:
        batch_op.drop_column('specialization')
        batch_op.alter_column(
            'compensation_type',
            existing_type=sa.Enum('project_salary', 'research_grant', 'volunteer', name='compensationtype'),
            type_=sa.Enum('project_salary', 'research_grant', name='compensationtype'),
            existing_nullable=True,
        )
        batch_op.alter_column(
            'role',
            existing_type=sa.Enum(
                'ceo', 'engineering_manager', 'project_manager', 'chief_scientist',
                'tech_lead', 'engineer', 'researcher', 'research_fellow', 'staff',
                name='labrole',
            ),
            type_=sa.Enum(
                'ceo', 'engineering_manager', 'project_manager', 'research_manager',
                'tech_lead', 'engineer', 'researcher', 'staff',
                name='labrole',
            ),
            existing_nullable=False,
        )

    # ── members table ────────────────────────────────────────────────────────
    with op.batch_alter_table('members', schema=None) as batch_op:
        batch_op.drop_index('ix_members_cpf')
        batch_op.drop_constraint('uq_members_cpf', type_='unique')
        batch_op.drop_column('is_professor')
        batch_op.drop_column('cpf')
