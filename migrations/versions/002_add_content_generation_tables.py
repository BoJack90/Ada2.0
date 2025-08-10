"""add_content_generation_tables

Revision ID: 002
Revises: 001
Create Date: 2025-01-10 10:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    # Create communication_strategies table
    op.create_table('communication_strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('organization_id', sa.Integer(), nullable=False),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, server_default='true'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organization_id'], ['organizations.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_communication_strategies_id'), 'communication_strategies', ['id'], unique=False)

    # Create personas table
    op.create_table('personas',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_personas_id'), 'personas', ['id'], unique=False)

    # Create platform_styles table
    op.create_table('platform_styles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('platform_name', sa.String(length=100), nullable=False),
        sa.Column('length_description', sa.Text(), nullable=False),
        sa.Column('style_description', sa.Text(), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_platform_styles_id'), 'platform_styles', ['id'], unique=False)

    # Create cta_rules table
    op.create_table('cta_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('cta_text', sa.String(length=500), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cta_rules_id'), 'cta_rules', ['id'], unique=False)

    # Create general_styles table
    op.create_table('general_styles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('language', sa.String(length=50), nullable=False),
        sa.Column('tone', sa.String(length=100), nullable=False),
        sa.Column('technical_content', sa.Text(), nullable=False),
        sa.Column('employer_branding_content', sa.Text(), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_general_styles_id'), 'general_styles', ['id'], unique=False)

    # Create communication_goals table
    op.create_table('communication_goals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('goal_text', sa.String(length=500), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_communication_goals_id'), 'communication_goals', ['id'], unique=False)

    # Create forbidden_phrases table
    op.create_table('forbidden_phrases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phrase', sa.String(length=200), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forbidden_phrases_id'), 'forbidden_phrases', ['id'], unique=False)

    # Create preferred_phrases table
    op.create_table('preferred_phrases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('phrase', sa.String(length=200), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_preferred_phrases_id'), 'preferred_phrases', ['id'], unique=False)

    # Create sample_content_types table
    op.create_table('sample_content_types',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('content_type', sa.String(length=100), nullable=False),
        sa.Column('communication_strategy_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['communication_strategy_id'], ['communication_strategies.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sample_content_types_id'), 'sample_content_types', ['id'], unique=False)


def downgrade():
    # Drop tables in reverse order
    op.drop_index(op.f('ix_sample_content_types_id'), table_name='sample_content_types')
    op.drop_table('sample_content_types')
    
    op.drop_index(op.f('ix_preferred_phrases_id'), table_name='preferred_phrases')
    op.drop_table('preferred_phrases')
    
    op.drop_index(op.f('ix_forbidden_phrases_id'), table_name='forbidden_phrases')
    op.drop_table('forbidden_phrases')
    
    op.drop_index(op.f('ix_communication_goals_id'), table_name='communication_goals')
    op.drop_table('communication_goals')
    
    op.drop_index(op.f('ix_general_styles_id'), table_name='general_styles')
    op.drop_table('general_styles')
    
    op.drop_index(op.f('ix_cta_rules_id'), table_name='cta_rules')
    op.drop_table('cta_rules')
    
    op.drop_index(op.f('ix_platform_styles_id'), table_name='platform_styles')
    op.drop_table('platform_styles')
    
    op.drop_index(op.f('ix_personas_id'), table_name='personas')
    op.drop_table('personas')
    
    op.drop_index(op.f('ix_communication_strategies_id'), table_name='communication_strategies')
    op.drop_table('communication_strategies') 