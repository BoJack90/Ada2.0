"""add_content_briefs_and_correlation

Revision ID: 018
Revises: 017
Create Date: 2025-01-17 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '018'
down_revision: Union[str, None] = '011_add_content_plans_indexes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add content briefs and correlation rules tables"""
    
    # Create content_briefs table
    op.create_table('content_briefs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_plan_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('file_path', sa.String(length=500), nullable=True),
        sa.Column('file_type', sa.String(length=50), nullable=True),
        sa.Column('extracted_content', sa.Text(), nullable=True),
        sa.Column('key_topics', sa.JSON(), nullable=True),
        sa.Column('priority_level', sa.Integer(), nullable=True),
        sa.Column('ai_analysis', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_plan_id'], ['content_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_briefs_content_plan_id'), 'content_briefs', ['content_plan_id'], unique=False)
    op.create_index(op.f('ix_content_briefs_id'), 'content_briefs', ['id'], unique=False)
    
    # Create content_correlation_rules table
    op.create_table('content_correlation_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_plan_id', sa.Integer(), nullable=False),
        sa.Column('rule_type', sa.String(length=50), nullable=True),
        sa.Column('sm_posts_per_blog', sa.Integer(), nullable=True),
        sa.Column('brief_based_sm_posts', sa.Integer(), nullable=True),
        sa.Column('standalone_sm_posts', sa.Integer(), nullable=True),
        sa.Column('platform_rules', sa.JSON(), nullable=True),
        sa.Column('correlation_strength', sa.String(length=20), nullable=True),
        sa.Column('timing_strategy', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['content_plan_id'], ['content_plans.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_content_correlation_rules_content_plan_id'), 'content_correlation_rules', ['content_plan_id'], unique=False)
    op.create_index(op.f('ix_content_correlation_rules_id'), 'content_correlation_rules', ['id'], unique=False)
    
    # Add metadata column to suggested_topics to track source
    op.add_column('suggested_topics', sa.Column('metadata', sa.JSON(), nullable=True))
    
    # Add AI prompts for brief analysis and generation
    connection = op.get_bind()
    
    # Brief analysis prompt
    brief_analysis_prompt = """Analyze the following content brief and extract key information:

Brief Content:
---
{brief_content}
---

Please extract and provide in JSON format:
1. "key_topics": List of main topics/themes (max 10)
2. "important_dates": Any mentioned dates or timeframes
3. "key_messages": Core messages to communicate
4. "target_focus": Specific audience or market segments mentioned
5. "priority_items": High-priority items or urgent matters
6. "content_suggestions": Suggested content ideas based on the brief
7. "context_summary": Brief summary of the context (max 200 words)

Respond ONLY with valid JSON."""
    
    connection.execute(
        sa.text("""
            INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
            VALUES (:prompt_name, :prompt_template, :version, :created_at, :updated_at)
        """),
        {
            'prompt_name': 'analyze_content_brief',
            'prompt_template': brief_analysis_prompt,
            'version': 1,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    )
    
    # Brief-based SM generation prompt
    sm_from_brief_prompt = """Based on the following brief insights, generate {count} social media post ideas:

Brief Context:
- Key Topics: {key_topics}
- Priority Items: {priority_items}
- Content Suggestions: {content_suggestions}

Generate engaging social media posts that address these topics and priorities.
Return as JSON array with objects containing "title" and "description"."""
    
    connection.execute(
        sa.text("""
            INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
            VALUES (:prompt_name, :prompt_template, :version, :created_at, :updated_at)
        """),
        {
            'prompt_name': 'generate_sm_from_brief',
            'prompt_template': sm_from_brief_prompt,
            'version': 1,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    )
    
    # Standalone SM generation prompt
    standalone_sm_prompt = """Generate {count} standalone social media post ideas for {organization_name} in the {industry} industry.

These should be engaging posts that are NOT related to any specific blog content, but rather:
- Company updates and news
- Industry insights and trends
- Tips and quick advice
- Engagement posts (questions, polls)
- Behind-the-scenes content
- Team highlights
- Customer success stories

Style: {style_info}

Return as JSON array with objects containing "title" and "description"."""
    
    connection.execute(
        sa.text("""
            INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
            VALUES (:prompt_name, :prompt_template, :version, :created_at, :updated_at)
        """),
        {
            'prompt_name': 'generate_standalone_sm',
            'prompt_template': standalone_sm_prompt,
            'version': 1,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    )
    
    # Add model assignments
    for task_name in ['analyze_content_brief', 'generate_sm_from_brief', 'generate_standalone_sm']:
        connection.execute(
            sa.text("""
                INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
                VALUES (:task_name, :model_name, :created_at, :updated_at)
            """),
            {
                'task_name': task_name,
                'model_name': 'gemini-1.5-pro-latest',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )


def downgrade() -> None:
    """Remove content briefs and correlation rules"""
    
    # Remove model assignments
    connection = op.get_bind()
    for task_name in ['analyze_content_brief', 'generate_sm_from_brief', 'generate_standalone_sm']:
        connection.execute(
            sa.text("DELETE FROM ai_model_assignments WHERE task_name = :task_name"),
            {'task_name': task_name}
        )
    
    # Remove prompts
    for prompt_name in ['analyze_content_brief', 'generate_sm_from_brief', 'generate_standalone_sm']:
        connection.execute(
            sa.text("DELETE FROM ai_prompts WHERE prompt_name = :prompt_name"),
            {'prompt_name': prompt_name}
        )
    
    # Drop metadata column from suggested_topics
    op.drop_column('suggested_topics', 'metadata')
    
    # Drop indexes and tables
    op.drop_index(op.f('ix_content_correlation_rules_id'), table_name='content_correlation_rules')
    op.drop_index(op.f('ix_content_correlation_rules_content_plan_id'), table_name='content_correlation_rules')
    op.drop_table('content_correlation_rules')
    
    op.drop_index(op.f('ix_content_briefs_id'), table_name='content_briefs')
    op.drop_index(op.f('ix_content_briefs_content_plan_id'), table_name='content_briefs')
    op.drop_table('content_briefs')