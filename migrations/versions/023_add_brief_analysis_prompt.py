"""Add brief analysis AI prompt

Revision ID: 023_add_brief_analysis_prompt
Revises: 022_add_missing_content_variant_columns
Create Date: 2025-01-28

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '023_add_brief_analysis_prompt'
down_revision = '022_add_missing_content_variant_columns'
branch_labels = None
depends_on = None


def upgrade():
    # Add AI prompt for brief analysis
    prompt_template = """Jesteś ekspertem analizy briefów marketingowych. Twoim zadaniem jest DOKŁADNA analiza briefu i wydobycie WSZYSTKICH kluczowych informacji, które będą INSTRUKCJAMI do generowania treści.

KRYTYCZNE: Brief zawiera KONKRETNE WYTYCZNE co do tematów i treści. MUSISZ je wszystkie zidentyfikować i oznaczyć jako OBOWIĄZKOWE do realizacji.

Brief do analizy:
---
{brief_content}
---

Przeanalizuj brief i wyodrębnij:

1. "mandatory_topics": OBOWIĄZKOWE tematy do realizacji (np. "system monitoringu zużycia energii", "symulacje CFD") - to są INSTRUKCJE, nie sugestie!
2. "key_topics": Pozostałe ważne tematy i zagadnienia
3. "important_dates": Daty, terminy, okresy (np. "sierpień")
4. "key_messages": Kluczowe komunikaty do przekazania
5. "target_focus": Grupy docelowe, segmenty rynku
6. "priority_items": Sprawy priorytetowe i pilne
7. "content_suggestions": Konkretne sugestie dotyczące treści
8. "company_news": Informacje o tym co dzieje się w firmie
9. "content_instructions": DOKŁADNE instrukcje jak tworzyć treści (np. "2 posty powinny zachęcać do przeczytania wpisów blogowych")
10. "context_summary": Podsumowanie briefu (max 200 słów)

WAŻNE: Jeśli brief mówi "zaproponuj tematy na temat X" - to X jest OBOWIĄZKOWYM tematem, nie sugestią!

Odpowiedz WYŁĄCZNIE poprawnym JSON-em."""
    
    now = datetime.utcnow()
    
    op.execute(
        f"""
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES ('analyze_content_brief', '{prompt_template.replace("'", "''")}', 1, '{now}', '{now}')
        """
    )
    
    # Add model assignment
    op.execute(
        f"""
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('analyze_content_brief', 'gemini-2.0-flash-exp', '{now}', '{now}')
        """
    )


def downgrade():
    op.execute("DELETE FROM ai_model_assignments WHERE task_name = 'analyze_content_brief'")
    op.execute("DELETE FROM ai_prompts WHERE prompt_name = 'analyze_content_brief'")