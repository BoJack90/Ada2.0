"""Add indexes for content_plans performance optimization

Revision ID: 011_add_content_plans_indexes
Revises: 010_add_brief_file_path_to_content_plans
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '011_add_content_plans_indexes'
down_revision = '010'
branch_labels = None
depends_on = None


def upgrade():
    # Indexes for content_plans table
    # Add index on organization_id for faster lookups
    op.create_index(
        'ix_content_plans_organization_id', 
        'content_plans', 
        ['organization_id']
    )
    
    # Add composite index for the common query pattern (organization_id + is_active)
    op.create_index(
        'ix_content_plans_org_active', 
        'content_plans', 
        ['organization_id', 'is_active']
    )
    
    # Add index on status for filtering
    op.create_index(
        'ix_content_plans_status',
        'content_plans',
        ['status']
    )
    
    # Add composite index for organization + status queries
    op.create_index(
        'ix_content_plans_org_status',
        'content_plans',
        ['organization_id', 'status', 'is_active']
    )
    
    # Indexes for suggested_topics table
    op.create_index(
        'ix_suggested_topics_content_plan_id',
        'suggested_topics',
        ['content_plan_id']
    )
    
    op.create_index(
        'ix_suggested_topics_plan_active',
        'suggested_topics',
        ['content_plan_id', 'is_active']
    )
    
    op.create_index(
        'ix_suggested_topics_plan_status',
        'suggested_topics',
        ['content_plan_id', 'status', 'is_active']
    )
    
    # Indexes for scheduled_posts table
    op.create_index(
        'ix_scheduled_posts_content_plan_id',
        'scheduled_posts',
        ['content_plan_id']
    )
    
    # Indexes for content_briefs table
    op.create_index(
        'ix_content_briefs_content_plan_id',
        'content_briefs',
        ['content_plan_id']
    )
    
    # Indexes for content_correlation_rules table
    op.create_index(
        'ix_content_correlation_rules_content_plan_id',
        'content_correlation_rules',
        ['content_plan_id']
    )


def downgrade():
    # Drop content_plans indexes
    op.drop_index('ix_content_plans_organization_id', 'content_plans')
    op.drop_index('ix_content_plans_org_active', 'content_plans')
    op.drop_index('ix_content_plans_status', 'content_plans')
    op.drop_index('ix_content_plans_org_status', 'content_plans')
    
    # Drop suggested_topics indexes
    op.drop_index('ix_suggested_topics_content_plan_id', 'suggested_topics')
    op.drop_index('ix_suggested_topics_plan_active', 'suggested_topics')
    op.drop_index('ix_suggested_topics_plan_status', 'suggested_topics')
    
    # Drop scheduled_posts indexes
    op.drop_index('ix_scheduled_posts_content_plan_id', 'scheduled_posts')
    
    # Drop content_briefs indexes
    op.drop_index('ix_content_briefs_content_plan_id', 'content_briefs')
    
    # Drop content_correlation_rules indexes
    op.drop_index('ix_content_correlation_rules_content_plan_id', 'content_correlation_rules')