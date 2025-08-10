"""Add meta_data columns to tables

Revision ID: 021_add_meta_data_columns
Revises: 020_rename_metadata_to_meta_data
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '021_add_meta_data_columns'
down_revision = '020_rename_metadata_to_meta_data'
branch_labels = None
depends_on = None


def upgrade():
    # Add meta_data column to content_plans if it doesn't exist
    op.add_column('content_plans', sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add meta_data column to suggested_topics if it doesn't exist
    op.add_column('suggested_topics', sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Add meta_data column to content_variants if it doesn't exist
    op.add_column('content_variants', sa.Column('meta_data', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade():
    # Remove meta_data columns
    op.drop_column('content_variants', 'meta_data')
    op.drop_column('suggested_topics', 'meta_data')
    op.drop_column('content_plans', 'meta_data')