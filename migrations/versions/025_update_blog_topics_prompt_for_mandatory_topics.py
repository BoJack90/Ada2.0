"""Update blog topics generation prompt to handle mandatory topics

Revision ID: 025_update_blog_topics_prompt_for_mandatory_topics
Revises: 024_update_analyze_content_brief_prompt
Create Date: 2025-01-28

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = '025_update_blog_topics_prompt_for_mandatory_topics'
down_revision = '024_update_analyze_content_brief_prompt'
branch_labels = None
depends_on = None


def upgrade():
    # Update the blog topics generation prompt to properly handle mandatory topics
    prompt_template = """Jesteś wybitnym strategiem content marketingu. Twoim zadaniem jest wygenerowanie propozycji tematów na wysokiej jakości, merytoryczne artykuły blogowe.

KRYTYCZNE WYMAGANIA:
1. MUSISZ uwzględnić WSZYSTKIE tematy z sekcji "mandatory_topics" w brief_insights
2. Jeśli brief określa konkretne instrukcje (content_instructions), MUSISZ je przestrzegać
3. Uwzględnij company_news i key_messages w generowanych tematach

Przeanalizuj dogłębnie dostarczony "Super-Kontekst", który zawiera:
- Strategię komunikacji klienta
- Cele i grupy docelowe
- Analizę briefów z OBOWIĄZKOWYMI tematami
- Dane z researchu

Kontekst:
---
{super_context}
---

INSTRUKCJE GENEROWANIA:
1. Najpierw wygeneruj tematy dla WSZYSTKICH mandatory_topics z brief_insights
2. Następnie dodaj tematy uzupełniające bazując na key_topics i pozostałych danych
3. Przestrzegaj content_instructions (np. ile postów ma zachęcać do czytania bloga)
4. Uwzględnij company_news w odpowiednich tematach
5. Wpleć key_messages w propozycje

Wygeneruj listę {topics_to_generate} tematów na artykuły blogowe. 

WAŻNE: Jeśli są mandatory_topics, to MUSZĄ być uwzględnione jako pierwsze!

Zwróć wynik **WYŁĄCZNIE** w formacie listy obiektów JSON. Każdy obiekt musi zawierać:
- "title": tytuł artykułu
- "description": opis co będzie zawierał artykuł (2-3 zdania)

Przykład:
[
  {
    "title": "System monitoringu zużycia energii - jak optymalizować koszty w firmie",
    "description": "Artykuł przedstawi innowacyjny system monitoringu energii, jego funkcjonalności i korzyści dla przedsiębiorstw. Omówimy przypadki użycia i ROI z wdrożenia."
  }
]"""
    
    now = datetime.utcnow()
    
    # Update the existing prompt
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{prompt_template.replace("'", "''")}',
            version = version + 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_blog_topics_for_selection'
        """
    )


def downgrade():
    # Revert to previous version
    prompt_template = """Jesteś wybitnym strategiem content marketingu. Twoim zadaniem jest wygenerowanie propozycji tematów na wysokiej jakości, merytoryczne artykuły blogowe.

Przeanalizuj dogłębnie dostarczony "Super-Kontekst", który zawiera strategię komunikacji klienta, jego cele, grupy docelowe, a także dane z researchu online.

Kontekst:
---
{super_context}
---

Na podstawie powyższego kontekstu, wygeneruj listę {topics_to_generate} angażujących i oryginalnych tematów na artykuły blogowe. Zwróć wynik **WYŁĄCZNIE** w formacie listy obiektów JSON. Każdy obiekt musi zawierać klucze: "title" i "description"."""
    
    now = datetime.utcnow()
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{prompt_template.replace("'", "''")}',
            version = version - 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_blog_topics_for_selection'
        """
    )