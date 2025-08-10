"""rename metadata columns to meta_data

Revision ID: 020_rename_metadata_to_meta_data
Revises: 019_add_advanced_generation_fields
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '020_rename_metadata_to_meta_data'
down_revision = '019_advanced_generation'
branch_labels = None
depends_on = None


def upgrade():
    """Rename metadata columns to meta_data to avoid SQLAlchemy reserved word conflict"""
    
    # Rename metadata column in suggested_topics table
    op.alter_column('suggested_topics', 'metadata',
                    new_column_name='meta_data',
                    existing_type=sa.JSON(),
                    existing_nullable=True)
    
    # Rename metadata column in content_plans table
    op.alter_column('content_plans', 'metadata',
                    new_column_name='meta_data',
                    existing_type=sa.JSON(),
                    existing_nullable=True)
    
    # Rename metadata column in content_variants table
    op.alter_column('content_variants', 'metadata',
                    new_column_name='meta_data',
                    existing_type=sa.JSON(),
                    existing_nullable=True)


def downgrade():
    """Revert meta_data columns back to metadata"""
    
    # Revert meta_data column in suggested_topics table
    op.alter_column('suggested_topics', 'meta_data',
                    new_column_name='metadata',
                    existing_type=sa.JSON(),
                    existing_nullable=True)
    
    # Revert meta_data column in content_plans table
    op.alter_column('content_plans', 'meta_data',
                    new_column_name='metadata',
                    existing_type=sa.JSON(),
                    existing_nullable=True)
    
    # Revert meta_data column in content_variants table
    op.alter_column('content_variants', 'meta_data',
                    new_column_name='metadata',
                    existing_type=sa.JSON(),
                    existing_nullable=True)