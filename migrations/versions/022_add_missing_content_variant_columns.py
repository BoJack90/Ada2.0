"""Add missing columns to content_variants table

Revision ID: 022_add_missing_content_variant_columns
Revises: 021_add_meta_data_columns
Create Date: 2025-01-24

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '022_add_missing_content_variant_columns'
down_revision = '021_add_meta_data_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Add missing columns to content_variants table
    op.add_column('content_variants', sa.Column('headline', sa.String(500), nullable=True))
    op.add_column('content_variants', sa.Column('cta_text', sa.String(500), nullable=True))
    op.add_column('content_variants', sa.Column('hashtags', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    op.add_column('content_variants', sa.Column('media_suggestions', postgresql.JSON(astext_type=sa.Text()), nullable=True))


def downgrade():
    # Remove columns
    op.drop_column('content_variants', 'media_suggestions')
    op.drop_column('content_variants', 'hashtags')
    op.drop_column('content_variants', 'cta_text')
    op.drop_column('content_variants', 'headline')