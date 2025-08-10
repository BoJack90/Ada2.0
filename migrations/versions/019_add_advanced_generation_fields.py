"""Add advanced content generation fields

Revision ID: 019_advanced_generation
Revises: 018_add_content_briefs_and_correlation
Create Date: 2024-01-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '019_advanced_generation'
down_revision = '018'
branch_labels = None
depends_on = None


def upgrade():
    # Add metadata field to SuggestedTopic for storing reasoning data
    op.add_column(
        'suggested_topics',
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Add new fields to ContentVariant
    op.add_column(
        'content_variants',
        sa.Column('headline', sa.String(500), nullable=True)
    )
    op.add_column(
        'content_variants',
        sa.Column('cta_text', sa.String(500), nullable=True)
    )
    op.add_column(
        'content_variants',
        sa.Column('hashtags', postgresql.JSONB, nullable=True)
    )
    op.add_column(
        'content_variants',
        sa.Column('media_suggestions', postgresql.JSONB, nullable=True)
    )
    op.add_column(
        'content_variants',
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Add metadata field to ContentPlan for generation settings
    op.add_column(
        'content_plans',
        sa.Column('metadata', postgresql.JSONB, nullable=True)
    )
    
    # Create research_results table
    op.create_table(
        'research_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('topic', sa.String(500), nullable=False),
        sa.Column('research_data', postgresql.JSONB, nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ondelete='CASCADE')
    )
    
    op.create_index('ix_research_results_organization_id', 'research_results', ['organization_id'])
    op.create_index('ix_research_results_topic', 'research_results', ['topic'])
    
    # Add new AI prompts for advanced generation
    op.execute("""
        INSERT INTO ai_prompts (name, prompt_text, description, created_at, updated_at)
        VALUES 
        ('deep_reasoning', 
         'Analyze the following context for content generation using step-by-step reasoning...', 
         'Deep reasoning analysis prompt for content understanding',
         NOW(), NOW()),
        
        ('research_analysis',
         'Based on the research data below, extract key insights for content creation...',
         'Research data analysis and synthesis prompt',
         NOW(), NOW()),
         
        ('strategy_formulation',
         'Based on the deep understanding and research, formulate a content strategy...',
         'Content strategy formulation prompt',
         NOW(), NOW()),
         
        ('creative_generation',
         'Based on the content strategy, generate creative blog topics...',
         'Creative content generation with strategy alignment',
         NOW(), NOW()),
         
        ('evaluation',
         'Evaluate and refine the generated topics using these criteria...',
         'Content evaluation and refinement prompt',
         NOW(), NOW()),
         
        ('brief_analysis',
         'Perform a comprehensive analysis of this content brief...',
         'Enhanced brief analysis with deep insights',
         NOW(), NOW()),
         
        ('generate_sm_from_brief',
         'Based on the following brief insights, generate social media post ideas...',
         'Generate SM content from brief insights',
         NOW(), NOW())
    """)
    
    # Add model assignments for new prompts
    op.execute("""
        INSERT INTO ai_model_assignments (prompt_name, model_name, created_at, updated_at)
        VALUES 
        ('deep_reasoning', 'gemini-1.5-pro-latest', NOW(), NOW()),
        ('research_analysis', 'gemini-1.5-pro-latest', NOW(), NOW()),
        ('strategy_formulation', 'gemini-1.5-pro-latest', NOW(), NOW()),
        ('creative_generation', 'gemini-1.5-pro-latest', NOW(), NOW()),
        ('evaluation', 'gemini-1.5-pro-latest', NOW(), NOW()),
        ('brief_analysis', 'gemini-1.5-pro-latest', NOW(), NOW()),
        ('generate_sm_from_brief', 'gemini-1.5-pro-latest', NOW(), NOW())
    """)
    
    # Add indexes for better performance
    op.create_index('ix_suggested_topics_metadata', 'suggested_topics', ['metadata'])
    op.create_index('ix_content_variants_metadata', 'content_variants', ['metadata'])


def downgrade():
    # Drop indexes
    op.drop_index('ix_suggested_topics_metadata', 'suggested_topics')
    op.drop_index('ix_content_variants_metadata', 'content_variants')
    op.drop_index('ix_research_results_organization_id', 'research_results')
    op.drop_index('ix_research_results_topic', 'research_results')
    
    # Drop research_results table
    op.drop_table('research_results')
    
    # Drop columns
    op.drop_column('content_plans', 'metadata')
    op.drop_column('content_variants', 'metadata')
    op.drop_column('content_variants', 'media_suggestions')
    op.drop_column('content_variants', 'hashtags')
    op.drop_column('content_variants', 'cta_text')
    op.drop_column('content_variants', 'headline')
    op.drop_column('suggested_topics', 'metadata')
    
    # Remove AI prompts
    op.execute("""
        DELETE FROM ai_model_assignments 
        WHERE prompt_name IN (
            'deep_reasoning', 'research_analysis', 'strategy_formulation',
            'creative_generation', 'evaluation', 'brief_analysis', 'generate_sm_from_brief'
        )
    """)
    
    op.execute("""
        DELETE FROM ai_prompts 
        WHERE name IN (
            'deep_reasoning', 'research_analysis', 'strategy_formulation',
            'creative_generation', 'evaluation', 'brief_analysis', 'generate_sm_from_brief'
        )
    """)