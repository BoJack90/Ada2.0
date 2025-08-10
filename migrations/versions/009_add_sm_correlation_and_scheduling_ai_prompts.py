"""add_sm_correlation_and_scheduling_ai_prompts

Revision ID: 009
Revises: 008
Create Date: 2025-01-14 11:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '009'
down_revision = '008'
branch_labels = None
depends_on = None


def upgrade():
    """Add AI prompts for SM correlation and scheduling functionality"""
    
    now = datetime.utcnow()
    
    # Prompt for generating correlated social media variants from blog context
    sm_correlation_prompt = """Jesteś strategiem social media. Twoim zadaniem jest stworzenie serii krótkich, angażujących postów, które będą promować i rozwijać poniższy, zaakceptowany temat na artykuł blogowy. Dla każdego tematu blogowego wygeneruj {sm_posts_per_blog} powiązanych tematycznie postów na social media.

Zaakceptowany temat na bloga, do którego masz nawiązać:
---
Tytuł: {blog_topic_title}
Opis: {blog_topic_description}
---

Pamiętaj o strategii i wytycznych dla platform social media. Zwróć wynik WYŁĄCZNIE w formacie listy obiektów JSON. Każdy obiekt musi zawierać klucze: "title" i "description"."""
    
    # Prompt for scheduling topics in calendar
    scheduling_prompt = """Jesteś menedżerem kalendarza redakcyjnego. Otrzymałeś finalną listę zaakceptowanych wariantów treści na {plan_period}. Twoim zadaniem jest rozplanowanie ich publikacji w kalendarzu.

Oto lista treści (wariantów) do zaplanowania:
---
{variants_list}
---

Oto zasady harmonogramu, których musisz przestrzegać:
---
{scheduling_preferences}
---

Stwórz harmonogram, uwzględniając zasady oraz logiczną kolejność (np. post zapowiadający przed artykułem na blogu). Zwróć wynik WYŁĄCZNIE w formacie listy obiektów JSON. Każdy obiekt musi zawierać klucze: "content_variant_id" i "publication_date" (w formacie YYYY-MM-DD HH:MM)."""
    
    # Insert prompts into ai_prompts table
    op.execute(
        """
        INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
        VALUES 
            ('generate_sm_variants_from_blog_context', %s, 1, %s, %s),
            ('schedule_topics', %s, 1, %s, %s)
        """,
        (sm_correlation_prompt, now, now, scheduling_prompt, now, now)
    )
    
    # Insert model assignments
    op.execute(
        """
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES 
            ('generate_sm_variants_from_blog_context', 'gemini-1.5-flash-latest', %s, %s),
            ('schedule_topics', 'gemini-1.5-pro-latest', %s, %s)
        """,
        (now, now, now, now)
    )


def downgrade():
    """Remove SM correlation and scheduling AI prompts"""
    
    # Remove model assignments first
    op.execute(
        """
        DELETE FROM ai_model_assignments 
        WHERE task_name IN ('generate_sm_variants_from_blog_context', 'schedule_topics')
        """
    )
    
    # Remove prompts
    op.execute(
        """
        DELETE FROM ai_prompts 
        WHERE prompt_name IN ('generate_sm_variants_from_blog_context', 'schedule_topics')
        """
    ) 