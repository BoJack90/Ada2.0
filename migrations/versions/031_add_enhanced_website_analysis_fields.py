"""Add enhanced website analysis fields

Revision ID: 031
Revises: 030
Create Date: 2025-01-10
"""
import sqlalchemy as sa
from alembic import op

# revision identifiers
revision = '031_add_enhanced_website_analysis_fields'
down_revision = '030_update_all_prompts_with_website_analysis'
branch_labels = None
depends_on = None

def upgrade():
    """Add new fields for enhanced website analysis"""
    
    # Add new columns to website_analysis table
    op.add_column('website_analysis', 
        sa.Column('unique_selling_points', sa.JSON(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('content_strategy_insights', sa.Text(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('recommended_content_topics', sa.JSON(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('brand_personality', sa.Text(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('key_differentiators', sa.JSON(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('market_positioning', sa.String(500), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('customer_pain_points', sa.JSON(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('technology_stack', sa.JSON(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('partnership_ecosystem', sa.JSON(), nullable=True))
    op.add_column('website_analysis', 
        sa.Column('company_overview', sa.Text(), nullable=True))
    
    print("✅ Added enhanced website analysis fields")

def downgrade():
    """Remove enhanced website analysis fields"""
    
    # Remove columns from website_analysis table
    op.drop_column('website_analysis', 'company_overview')
    op.drop_column('website_analysis', 'partnership_ecosystem')
    op.drop_column('website_analysis', 'technology_stack')
    op.drop_column('website_analysis', 'customer_pain_points')
    op.drop_column('website_analysis', 'market_positioning')
    op.drop_column('website_analysis', 'key_differentiators')
    op.drop_column('website_analysis', 'brand_personality')
    op.drop_column('website_analysis', 'recommended_content_topics')
    op.drop_column('website_analysis', 'content_strategy_insights')
    op.drop_column('website_analysis', 'unique_selling_points')
    
    print("✅ Removed enhanced website analysis fields")