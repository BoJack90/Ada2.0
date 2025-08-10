"""add_ai_prompts_and_model_assignments

Revision ID: 001
Revises: 
Create Date: 2025-01-10 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create ai_prompts table
    op.create_table('ai_prompts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('prompt_name', sa.String(length=100), nullable=False),
        sa.Column('prompt_template', sa.Text(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_prompts_id'), 'ai_prompts', ['id'], unique=False)
    op.create_index(op.f('ix_ai_prompts_prompt_name'), 'ai_prompts', ['prompt_name'], unique=True)

    # Create ai_model_assignments table
    op.create_table('ai_model_assignments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=100), nullable=False),
        sa.Column('model_name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_model_assignments_id'), 'ai_model_assignments', ['id'], unique=False)
    op.create_index(op.f('ix_ai_model_assignments_task_name'), 'ai_model_assignments', ['task_name'], unique=True)

    # Insert seed data
    now = datetime.utcnow()
    
    # Seed data for ai_prompts
    op.execute(
        """
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES ('strategy_parser', 
                'Jesteś ekspertem w analizie strategii marketingowych. Przeanalizuj następujący tekst i wyodrębnij kluczowe elementy strategii:

{strategy_text}

Proszę zwróć wynik w formacie JSON z następującymi polami:
- "goal": główny cel strategii
- "target_audience": grupa docelowa
- "channels": kanały marketingowe
- "budget": budżet (jeśli podany)
- "timeline": harmonogram (jeśli podany)
- "kpis": kluczowe wskaźniki wydajności
- "risks": potencjalne ryzyka

Odpowiedź powinna być w języku polskim.',
                1, 
                %s, 
                %s)
        """,
        (now, now)
    )
    
    # Seed data for ai_model_assignments
    op.execute(
        """
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('strategy_parser', 'gemini-1.5-pro-latest', %s, %s)
        """,
        (now, now)
    )


def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_ai_model_assignments_task_name'), table_name='ai_model_assignments')
    op.drop_index(op.f('ix_ai_model_assignments_id'), table_name='ai_model_assignments')
    op.drop_index(op.f('ix_ai_prompts_prompt_name'), table_name='ai_prompts')
    op.drop_index(op.f('ix_ai_prompts_id'), table_name='ai_prompts')
    
    # Drop tables
    op.drop_table('ai_model_assignments')
    op.drop_table('ai_prompts') 