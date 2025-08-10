"""Update all content generation prompts to include website analysis

Revision ID: 030_update_all_prompts_with_website_analysis
Revises: 029_update_blog_topics_prompt_with_website_analysis
Create Date: 2025-01-10

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '030_update_all_prompts_with_website_analysis'
down_revision = '029_update_blog_topics_prompt_with_website_analysis'
branch_labels = None
depends_on = None


def upgrade():
    now = datetime.utcnow()
    
    # 1. Update generate_initial_draft prompt
    generate_initial_draft_template = """Jesteś wybitnym copywriterem i specjalistą content marketingu. Twoim zadaniem jest napisanie wysokiej jakości artykułu blogowego.

KONTEKST ORGANIZACJI I STRATEGII:
{context_data}

SZCZEGÓŁY POSTA:
{post_details}

INSTRUKCJE:
1. Wykorzystaj informacje z analizy strony internetowej (website_analysis) jeśli dostępne:
   - Dopasuj ton do content_tone z analizy strony
   - Uwzględnij services_detected w treści
   - Nawiąż do company_values i key_topics
   - Dostosuj treść do target_audience

2. Napisz kompletny artykuł blogowy (3000-6000 znaków)
3. Zachowaj strukturę: wstęp, rozwinięcie z nagłówkami, podsumowanie
4. Używaj języka i tonu zgodnego ze strategią komunikacji
5. Unikaj bezpośredniej sprzedaży - skup się na wartości merytorycznej
6. Zakończ subtelnym CTA zachęcającym do kontaktu

Zwróć artykuł w formacie Markdown z odpowiednimi nagłówkami (##, ###)."""
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{generate_initial_draft_template.replace("'", "''")}',
            version = version + 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_initial_draft'
        """
    )
    
    # 2. Update generate_single_variant prompt  
    generate_single_variant_template = """Jesteś ekspertem w tworzeniu angażujących treści na różne platformy. Twoim zadaniem jest stworzenie wariantu treści.

KONTEKST TEMATU:
{topic_context}

STRATEGIA KOMUNIKACJI:
{strategy_context}

KONTEKST CZASOWY:
{temporal_context}

PLATFORMA DOCELOWA:
{platform_rules}

INSTRUKCJE:
1. Jeśli dostępna jest analiza strony internetowej w kontekście strategii:
   - Wykorzystaj informacje o oferowanych usługach
   - Nawiąż do wartości firmy
   - Dopasuj ton do tego z analizy strony
   - Uwzględnij kluczowe tematy ze strony

2. Stwórz angażującą treść dopasowaną do platformy
3. Zachowaj spójność ze strategią komunikacji
4. Użyj odpowiednich hashtagów dla social media
5. Dodaj emotikony gdzie właściwe
6. Zakończ call-to-action

WYMAGANY FORMAT ODPOWIEDZI:
{{
  "content": "Treść posta",
  "hashtags": ["hashtag1", "hashtag2"],
  "media_suggestions": ["sugestia1", "sugestia2"]
}}"""
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{generate_single_variant_template.replace("'", "''")}',
            version = version + 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_single_variant'
        """
    )
    
    # 3. Update generate_standalone_sm prompt
    generate_standalone_sm_template = """Wygeneruj {{count}} pomysłów na samodzielne posty w mediach społecznościowych dla {{organization_name}} z branży {{industry}}.

Posty powinny być angażujące i NIE związane z konkretnymi artykułami blogowymi, ale raczej:
- Aktualności i nowości firmy
- Trendy i insights branżowe
- Porady i szybkie wskazówki
- Posty angażujące (pytania, ankiety)
- Kulisy firmy
- Wyróżnienia zespołu
- Historie sukcesu klientów

Styl: {{style_info}}

{{website_context}}

INSTRUKCJE:
1. Wykorzystaj kontekst z analizy strony internetowej jeśli dostępny
2. Nawiąż do usług, wartości i kluczowych tematów firmy
3. Dopasuj ton do tego wykrytego na stronie
4. Uwzględnij grupę docelową

Zwróć jako tablicę JSON z obiektami zawierającymi "title" i "description"."""
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{generate_standalone_sm_template.replace("'", "''")}',
            version = version + 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_standalone_sm'
        """
    )
    
    print("✅ Updated content generation prompts to include website analysis context")


def downgrade():
    now = datetime.utcnow()
    
    # Revert generate_initial_draft
    old_initial_draft = """Jesteś wybitnym copywriterem i specjalistą content marketingu. Twoim zadaniem jest napisanie wysokiej jakości artykułu blogowego.

KONTEKST ORGANIZACJI I STRATEGII:
{context_data}

SZCZEGÓŁY POSTA:
{post_details}

Napisz kompletny artykuł blogowy (3000-6000 znaków) zachowując:
- Strukturę: wstęp, rozwinięcie z nagłówkami, podsumowanie
- Język i ton zgodny ze strategią komunikacji
- Wartość merytoryczną bez bezpośredniej sprzedaży
- Subtelne CTA na końcu

Zwróć artykuł w formacie Markdown."""
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{old_initial_draft.replace("'", "''")}',
            version = version - 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_initial_draft'
        """
    )
    
    # Revert generate_single_variant
    old_single_variant = """Jesteś ekspertem w tworzeniu angażujących treści na różne platformy.

KONTEKST TEMATU:
{topic_context}

STRATEGIA KOMUNIKACJI:
{strategy_context}

KONTEKST CZASOWY:
{temporal_context}

PLATFORMA DOCELOWA:
{platform_rules}

Stwórz angażującą treść dopasowaną do platformy, zachowując spójność ze strategią.

WYMAGANY FORMAT:
{{
  "content": "Treść posta",
  "hashtags": ["hashtag1", "hashtag2"],
  "media_suggestions": ["sugestia1", "sugestia2"]
}}"""
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{old_single_variant.replace("'", "''")}',
            version = version - 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_single_variant'
        """
    )
    
    # Revert generate_standalone_sm
    old_standalone_sm = """Generate {{count}} standalone social media post ideas for {{organization_name}} in the {{industry}} industry.

These should be engaging posts that are NOT related to any specific blog content, but rather:
- Company updates and news
- Industry insights and trends
- Tips and quick advice
- Engagement posts (questions, polls)
- Behind-the-scenes content
- Team highlights
- Customer success stories

Style: {{style_info}}

Return as JSON array with objects containing "title" and "description"."""
    
    op.execute(
        f"""
        UPDATE ai_prompts 
        SET prompt_template = '{old_standalone_sm.replace("'", "''")}',
            version = version - 1,
            updated_at = '{now}'
        WHERE prompt_name = 'generate_standalone_sm'
        """
    )
    
    print("✅ Reverted content generation prompts")