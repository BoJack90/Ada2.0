"""add_blog_topics_generation_ai_task

Revision ID: 006
Revises: 005
Create Date: 2025-01-11 17:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add AI prompt and model assignment for blog topics generation"""
    
    # Połączenie z bazą danych
    connection = op.get_bind()
    
    # Dodaj nowy prompt do tabeli ai_prompts
    blog_topics_prompt = """Jesteś wybitnym strategiem content marketingu. Twoim zadaniem jest wygenerowanie propozycji tematów na wysokiej jakości, merytoryczne artykuły blogowe.

Przeanalizuj dogłębnie dostarczony "Super-Kontekst", który zawiera strategię komunikacji klienta, jego cele, grupy docelowe, a także dane z researchu online.

Kontekst:
---
{super_context}
---

Na podstawie powyższego kontekstu, wygeneruj listę {topics_to_generate} angażujących i oryginalnych tematów na artykuły blogowe. Zwróć wynik **WYŁĄCZNIE** w formacie listy obiektów JSON. Każdy obiekt musi zawierać klucze: "title" i "description"."""

    connection.execute(
        sa.text("""
            INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
            VALUES (:prompt_name, :prompt_template, :version, :created_at, :updated_at)
        """),
        {
            'prompt_name': 'generate_blog_topics_for_selection',
            'prompt_template': blog_topics_prompt,
            'version': 1,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    )
    
    # Dodaj mapping zadania do modelu AI
    connection.execute(
        sa.text("""
            INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
            VALUES (:task_name, :model_name, :created_at, :updated_at)
        """),
        {
            'task_name': 'generate_blog_topics_for_selection',
            'model_name': 'gemini-1.5-pro-latest',
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
    )


def downgrade() -> None:
    """Remove AI prompt and model assignment for blog topics generation"""
    
    # Połączenie z bazą danych
    connection = op.get_bind()
    
    # Usuń model assignment
    connection.execute(
        sa.text("DELETE FROM ai_model_assignments WHERE task_name = :task_name"),
        {'task_name': 'generate_blog_topics_for_selection'}
    )
    
    # Usuń prompt
    connection.execute(
        sa.text("DELETE FROM ai_prompts WHERE prompt_name = :prompt_name"),
        {'prompt_name': 'generate_blog_topics_for_selection'}
    ) 