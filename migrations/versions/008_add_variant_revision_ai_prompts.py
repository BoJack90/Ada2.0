"""add_variant_revision_ai_prompts

Revision ID: 008
Revises: 007
Create Date: 2025-01-14 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '008'
down_revision = '007'
branch_labels = None
depends_on = None


def upgrade():
    """Add AI prompts for variant revision functionality"""
    
    now = datetime.utcnow()
    
    # Prompt for revising variant based on feedback
    feedback_prompt = """Jesteś światowej klasy ekspertem od content marketingu i copywriterem. Otrzymałeś feedback od klienta na temat swojego posta i musisz go poprawić, uwzględniając wszystkie uwagi.

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

**Polecenie:** Stwórz poprawioną wersję posta, która uwzględnia feedback i jest w 100% zgodna ze wszystkimi powyższymi wytycznymi. Zwróć wynik **WYŁĄCZNIE** w formacie obiektu JSON z jednym kluczem: "content_text"."""
    
    # Prompt for regenerating variant
    regenerate_prompt = """Jesteś światowej klasy ekspertem od content marketingu i copywriterem. Poprzednia wersja posta została odrzucona i musisz stworzyć nową, lepszą wersję na ten sam temat.

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

**Polecenie:** Stwórz nową, ulepszoną wersję posta, która jest w 100% zgodna ze wszystkimi powyższymi wytycznymi. Podejdź do tematu z innej strony niż poprzednio. Zwróć wynik **WYŁĄCZNIE** w formacie obiektu JSON z jednym kluczem: "content_text"."""
    
    # Insert prompts into ai_prompts table
    op.execute(
        """
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES 
            ('revise_single_variant_with_feedback', %s, 1, %s, %s),
            ('regenerate_single_variant', %s, 1, %s, %s)
        """,
        (feedback_prompt, now, now, regenerate_prompt, now, now)
    )
    
    # Insert model assignments
    op.execute(
        """
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES 
            ('revise_single_variant_with_feedback', 'gemini-1.5-pro-latest', %s, %s),
            ('regenerate_single_variant', 'gemini-1.5-pro-latest', %s, %s)
        """,
        (now, now, now, now)
    )


def downgrade():
    """Remove variant revision AI prompts"""
    
    # Remove model assignments first
    op.execute(
        """
        DELETE FROM ai_model_assignments 
        WHERE task_name IN ('revise_single_variant_with_feedback', 'regenerate_single_variant')
        """
    )
    
    # Remove prompts
    op.execute(
        """
        DELETE FROM ai_prompts 
        WHERE prompt_name IN ('revise_single_variant_with_feedback', 'regenerate_single_variant')
        """
    ) 