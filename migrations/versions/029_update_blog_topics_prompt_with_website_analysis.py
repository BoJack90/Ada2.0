"""Update blog topics prompt to include website analysis context

Revision ID: 029_update_blog_topics_prompt_with_website_analysis
Revises: 028_add_website_analysis_table
Create Date: 2025-01-10

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '029_update_blog_topics_prompt_with_website_analysis'
down_revision = '028_add_website_analysis'
branch_labels = None
depends_on = None


def upgrade():
    # Update the prompt to include website analysis context
    prompt_template = """Jesteś wybitnym strategiem content marketingu. Twoim zadaniem jest wygenerowanie propozycji tematów na wysokiej jakości, merytoryczne artykuły blogowe.

KRYTYCZNE WYMAGANIA:
1. MUSISZ uwzględnić WSZYSTKIE tematy z sekcji "mandatory_topics" w brief_insights
2. Jeśli brief określa konkretne instrukcje (content_instructions), MUSISZ je przestrzegać
3. Uwzględnij company_news i key_messages w generowanych tematach
4. Wykorzystaj informacje z analizy strony internetowej (website_insights) jeśli dostępne

Przeanalizuj dogłębnie dostarczony "Super-Kontekst", który zawiera:
- Informacje o organizacji (nazwa, branża, opis)
- Analizę strony internetowej (usługi, wartości, ton komunikacji, kluczowe tematy)
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
2. Wykorzystaj website_insights do lepszego zrozumienia firmy:
   - services_detected: usługi oferowane przez firmę
   - company_values: wartości i misja firmy
   - key_topics: tematy poruszane na stronie
   - content_tone: ton komunikacji na stronie
   - target_audience: grupa docelowa
3. Następnie dodaj tematy uzupełniające bazując na key_topics i pozostałych danych
4. Przestrzegaj content_instructions (np. ile postów ma zachęcać do czytania bloga)
5. Uwzględnij company_news w odpowiednich tematach
6. Wpleć key_messages w propozycje
7. Dopasuj ton i styl do tego, co widać na stronie internetowej firmy

Wygeneruj listę {topics_to_generate} tematów na artykuły blogowe. 

WAŻNE: 
- Jeśli są mandatory_topics, to MUSZĄ być uwzględnione jako pierwsze!
- Jeśli dostępne są website_insights, wykorzystaj je do lepszego dopasowania tematów

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
    
    print("✅ Updated blog topics generation prompt to include website analysis context")


def downgrade():
    # Revert to previous version
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
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{prompt_template.replace("'", "''")}',
            version = version - 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_blog_topics_for_selection'
        """
    )
    
    print("✅ Reverted blog topics generation prompt")