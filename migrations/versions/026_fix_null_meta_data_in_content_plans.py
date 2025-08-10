"""Fix null meta_data in existing content_plans

Revision ID: 026_fix_null_meta_data_in_content_plans
Revises: 025_update_blog_topics_prompt_for_mandatory_topics
Create Date: 2025-01-28

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '026_fix_null_meta_data_in_content_plans'
down_revision = '025_update_blog_topics_prompt_for_mandatory_topics'
branch_labels = None
depends_on = None


def upgrade():
    # Update all content_plans with null meta_data to have empty JSON object
    op.execute(
        """
        UPDATE content_plans 
        SET meta_data = '{}'::jsonb 
        WHERE meta_data IS NULL
        """
    )
    
    # Also update suggested_topics and content_variants
    op.execute(
        """
        UPDATE suggested_topics 
        SET meta_data = '{}'::jsonb 
        WHERE meta_data IS NULL
        """
    )
    
    op.execute(
        """
        UPDATE content_variants 
        SET meta_data = '{}'::jsonb 
        WHERE meta_data IS NULL
        """
    )


def downgrade():
    # No need to revert empty objects back to NULL
    pass