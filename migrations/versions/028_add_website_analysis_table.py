"""Add website analysis table

Revision ID: 028_add_website_analysis
Revises: 027_add_organization_prompts
Create Date: 2025-01-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '028_add_website_analysis'
down_revision = '027_add_organization_prompts'
branch_labels = None
depends_on = None


def upgrade():
    # Create website_analysis table
    op.create_table(
        'website_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('website_url', sa.String(500), nullable=False),
        sa.Column('analysis_data', sa.JSON(), nullable=True),
        sa.Column('industry_detected', sa.String(200), nullable=True),
        sa.Column('services_detected', sa.JSON(), nullable=True),
        sa.Column('company_values', sa.JSON(), nullable=True),
        sa.Column('target_audience', sa.JSON(), nullable=True),
        sa.Column('content_tone', sa.String(200), nullable=True),
        sa.Column('key_topics', sa.JSON(), nullable=True),
        sa.Column('competitors_mentioned', sa.JSON(), nullable=True),
        sa.Column('last_analysis_date', sa.DateTime(), nullable=True),
        sa.Column('analysis_status', sa.String(50), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Add foreign key to organizations table
    op.create_foreign_key(
        'fk_website_analysis_organization',
        'website_analysis',
        'organizations',
        ['organization_id'],
        ['id'],
        ondelete='CASCADE'
    )
    
    # Create index for faster lookups
    op.create_index(
        'ix_website_analysis_organization_id',
        'website_analysis',
        ['organization_id']
    )
    
    # Create unique constraint - one analysis per organization
    op.create_unique_constraint(
        'uq_website_analysis_organization_id',
        'website_analysis',
        ['organization_id']
    )
    
    print("✅ Created website_analysis table")


def downgrade():
    # Drop the table and all its constraints
    op.drop_index('ix_website_analysis_organization_id', table_name='website_analysis')
    op.drop_table('website_analysis')
    
    print("✅ Dropped website_analysis table")