"""add_generate_single_variant_ai_prompt

Revision ID: cb2c414e9741
Revises: 009
Create Date: 2025-07-12 13:18:13.924042

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = 'cb2c414e9741'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Dodaj nowy prompt AI dla generowania pojedynczych wariantów
    prompt_template = """Jesteś światowej klasy ekspertem od content marketingu i copywriterem, który potrafi perfekcyjnie dostosować przekaz do specyfiki różnych platform. Twoim zadaniem jest stworzenie wersji roboczej posta na podstawie tematu, ogólnej strategii klienta oraz ścisłych wytycznych dla konkretnej platformy.

---
**TEMAT GŁÓWNY:**
Tytuł: {topic_title}
Opis: {topic_description}
---
**OGÓLNA STRATEGIA KLIENTA:**
{general_strategy_context}
---
**WYTYCZNE DLA PLATFORMY: {platform_name}**
{platform_rules}
---

**Polecenie:** Stwórz angażujący i wartościowy tekst wersji roboczej, który jest w 100% zgodny ze wszystkimi powyższymi wytycznymi. Zwróć wynik **WYŁĄCZNIE** w formacie obiektu JSON z jednym kluczem: "content_text"."""

    # Wstaw prompt do tabeli ai_prompts
    escaped_prompt = prompt_template.replace("'", "''")  # Escape single quotes for SQL
    op.execute(
        text(f"""
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES ('generate_single_variant', '{escaped_prompt}', 1, NOW(), NOW())
        """)
    )
    
    # Wstaw mapowanie modelu do tabeli ai_model_assignments
    op.execute(
        text("""
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('generate_single_variant', 'gemini-1.5-pro-latest', NOW(), NOW())
        """)
    )


def downgrade() -> None:
    # Usuń wpisy w kolejności odwrotnej
    op.execute(
        text("DELETE FROM ai_model_assignments WHERE task_name = 'generate_single_variant'")
    )
    
    op.execute(
        text("DELETE FROM ai_prompts WHERE prompt_name = 'generate_single_variant'")
    ) 