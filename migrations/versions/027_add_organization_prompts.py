"""add_organization_prompts

Revision ID: 027
Revises: 026
Create Date: 2025-07-31 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '027_add_organization_prompts'
down_revision = '026_fix_null_meta_data_in_content_plans'
branch_labels = None
depends_on = None


def upgrade():
    # Create organization_ai_prompts table for custom prompts per organization
    op.create_table('organization_ai_prompts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('prompt_name', sa.String(length=100), nullable=False),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('base_prompt_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['base_prompt_id'], ['ai_prompts.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_ai_prompts_id'), 'organization_ai_prompts', ['id'], unique=False)
    op.create_index(op.f('ix_organization_ai_prompts_organization_id'), 'organization_ai_prompts', ['organization_id'], unique=False)
    op.create_index('ix_org_prompt_unique', 'organization_ai_prompts', ['organization_id', 'prompt_name'], unique=True)
    
    # Create organization_ai_model_assignments table
    op.create_table('organization_ai_model_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('base_assignment_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['base_assignment_id'], ['ai_model_assignments.id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organization_ai_model_assignments_id'), 'organization_ai_model_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_organization_ai_model_assignments_organization_id'), 'organization_ai_model_assignments', ['organization_id'], unique=False)
    op.create_index('ix_org_model_unique', 'organization_ai_model_assignments', ['organization_id', 'task_name'], unique=True)
    
    # Add description columns to base tables
    op.add_column('ai_prompts', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('ai_model_assignments', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Remove columns from base tables
    op.drop_column('ai_model_assignments', 'description')
    op.drop_column('ai_prompts', 'description')
    
    # Drop indexes first
    op.drop_index('ix_org_model_unique', table_name='organization_ai_model_assignments')
    op.drop_index(op.f('ix_organization_ai_model_assignments_organization_id'), table_name='organization_ai_model_assignments')
    op.drop_index(op.f('ix_organization_ai_model_assignments_id'), table_name='organization_ai_model_assignments')
    
    op.drop_index('ix_org_prompt_unique', table_name='organization_ai_prompts')
    op.drop_index(op.f('ix_organization_ai_prompts_organization_id'), table_name='organization_ai_prompts')
    op.drop_index(op.f('ix_organization_ai_prompts_id'), table_name='organization_ai_prompts')
    
    # Drop tables
    op.drop_table('organization_ai_model_assignments')
    op.drop_table('organization_ai_prompts')