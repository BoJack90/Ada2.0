"""Ensure all AI prompts exist in database for clean installation

Revision ID: 032
Revises: 031
Create Date: 2025-08-10

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text
from datetime import datetime

# revision identifiers
revision = '032'
down_revision = '031'
branch_labels = None
depends_on = None

def upgrade():
    """Create or update all AI prompts to ensure they exist after clean installation"""
    
    connection = op.get_bind()
    
    # Dictionary of all prompts that should exist in the system
    # prompt_name: (version, prompt_template, description)
    all_prompts = {
        'strategy_parser': (1, 
            '''Jesteś ekspertem w analizie strategii komunikacji. Przeanalizuj plik i wyodrębnij kluczowe informacje.

Zwróć odpowiedź w formacie JSON zawierającym:
- strategy_name: nazwa strategii
- description: opis strategii
- communication_goals: lista celów komunikacyjnych
- target_audiences: lista grup docelowych z opisami
- general_style: ogólny styl komunikacji
- platform_styles: style dla różnych platform
- forbidden_phrases: lista zakazanych fraz
- preferred_phrases: lista preferowanych fraz
- cta_rules: zasady call-to-action''',
            'Analizuje dokumenty strategii komunikacji'),
            
        'analyze_content_brief': (1,
            '''Przeanalizuj brief contentu i wyodrębnij:
1. Obowiązkowe tematy do uwzględnienia
2. Instrukcje dotyczące treści
3. Wiadomości od firmy
4. Kluczowe przekazy
5. Priorytety

Zwróć w formacie JSON z kluczami:
- mandatory_topics
- content_instructions
- company_news
- key_messages
- priority_items''',
            'Analizuje briefy contentu'),
            
        'generate_blog_topics_for_selection': (1,
            '''Wygeneruj {topics_count} propozycji tematów blogowych.
Uwzględnij:
- Branżę: {industry}
- Strategię komunikacji: {communication_strategy}
- Analizę strony internetowej: {website_insights}
- Brief: {brief_insights}

Każdy temat powinien zawierać:
- title: tytuł
- description: opis
- content_type: "artykuł blogowy"
- reasoning: uzasadnienie''',
            'Generuje propozycje tematów blogowych'),
            
        'generate_single_variant': (1,
            '''Stwórz wariant treści dla platformy {platform}.
Temat: {topic_title}
Opis: {topic_description}
Kontekst: {super_context}

Dostosuj:
- Długość do platformy
- Styl komunikacji
- Format (hashtagi, emotikony)
- CTA odpowiednie dla platformy''',
            'Generuje pojedynczy wariant treści'),
            
        'generate_sm_variants_from_blog_context': (1,
            '''Na podstawie tematów blogowych wygeneruj skorelowane posty social media.
Tematy blogowe: {blog_topics}
Platformy: {platforms}

Dla każdego tematu stwórz warianty:
- LinkedIn: profesjonalny, merytoryczny
- Facebook: przystępny, angażujący
- Instagram: wizualny, lifestyle''',
            'Generuje posty SM skorelowane z blogiem'),
            
        'schedule_topics': (1,
            '''Zaplanuj harmonogram publikacji dla:
- {blog_count} postów blogowych
- {sm_count} postów social media
Okres: {period}

Rozmieść równomiernie w czasie.
Blog: poniedziałki i czwartki
Social: codziennie oprócz weekendów''',
            'Planuje harmonogram publikacji'),
            
        'generate_tavily_queries': (1,
            '''Na podstawie tematu: {topic}
Wygeneruj 3-4 zapytania wyszukiwania dla Tavily API.

Zapytania powinny być:
1. Konkretne i branżowe
2. Aktualne (2024/2025)
3. Praktyczne (case studies, statystyki)
4. Zróżnicowane aspekty tematu

Zwróć listę zapytań, każde w nowej linii.''',
            'Generuje zapytania dla Tavily API'),
            
        'generate_sm_from_brief': (1,
            '''Stwórz post social media bezpośrednio z briefu.
Brief: {brief_content}
Platforma: {platform}
Strategia: {communication_strategy}

Utwórz angażujący post:
- Nawiązujący do briefu
- Zgodny ze strategią
- Dostosowany do platformy''',
            'Generuje SM z briefu'),
            
        'generate_standalone_sm_posts': (1,
            '''Wygeneruj {count} samodzielnych postów SM.
Platforma: {platform}
Strategia: {communication_strategy}
Tematy: {suggested_topics}

Twórz różnorodne treści:
- Edukacyjne
- Angażujące
- Promocyjne
- Lifestyle''',
            'Generuje samodzielne posty SM'),
            
        'contextualize_content': (1,
            '''Dostosuj treść do kontekstu:
Treść: {content}
Kontekst: {context}
Cel: {purpose}

Zachowaj sens, ale dostosuj:
- Ton
- Szczegółowość
- Przykłady''',
            'Kontekstualizuje treść'),
            
        'generate_blog_content': (1,
            '''Napisz pełny artykuł blogowy.
Temat: {topic}
Słowa kluczowe: {keywords}
Długość: {word_count} słów

Struktura:
1. Wstęp
2. Rozwinięcie (3-4 sekcje)
3. Podsumowanie
4. CTA''',
            'Generuje pełne artykuły blogowe'),
            
        'generate_content_plan': (1,
            '''Stwórz plan contentu na {period}.
Liczba postów: {post_count}
Platformy: {platforms}

Uwzględnij:
- Różnorodność tematów
- Balans treści
- Święta i wydarzenia''',
            'Generuje plany contentu'),
            
        'generate_social_media_variant': (1,
            '''Przekształć treść na post SM.
Treść źródłowa: {source_content}
Platforma: {platform}

Skróć i dostosuj:
- Długość
- Hashtagi
- Emotikony
- CTA''',
            'Tworzy warianty SM z treści'),
            
        'revise_content_variant': (1,
            '''Popraw wariant treści.
Treść: {content}
Feedback: {feedback}
Wytyczne: {guidelines}

Zastosuj sugestie zachowując:
- Główny przekaz
- Styl marki''',
            'Poprawia warianty treści'),
            
        'regenerate_single_variant': (1,
            '''Wygeneruj wariant od nowa.
Poprzednia wersja: {previous_version}
Powód odrzucenia: {rejection_reason}

Stwórz zupełnie nową wersję:
- Inny angle
- Inna struktura
- Ten sam cel''',
            'Regeneruje odrzucone warianty'),
            
        'generate_initial_draft': (1,
            '''Stwórz wersję roboczą treści.
Typ: {content_type}
Temat: {topic_title}
Opis: {topic_description}
Kontekst: {super_context}

Struktura:
1. Wprowadzenie
2. Rozwinięcie
3. Podsumowanie
4. CTA

Długość: {word_count} słów''',
            'Generuje początkowe wersje treści'),
            
        'revise_draft_with_feedback': (1,
            '''Popraw wersję roboczą.
Treść: {current_draft}
Feedback: {operator_feedback}
Wytyczne: {revision_guidelines}

Zastosuj uwagi:
- Zachowaj mocne strony
- Popraw wskazane elementy
- Utrzymaj spójność''',
            'Poprawia drafty na podstawie feedbacku'),
            
        'regenerate_draft_from_rejection': (1,
            '''Stwórz draft od nowa po odrzuceniu.
Odrzucona wersja: {rejected_draft}
Powód: {rejection_reason}
Specyfikacja: {original_spec}

Całkowicie nowe podejście:
- Inny ton
- Inna perspektywa
- Nowa struktura''',
            'Regeneruje odrzucone drafty'),
            
        'revise_single_variant_with_feedback': (1,
            '''Popraw wariant na podstawie feedbacku.
Wariant: {current_variant}
Feedback: {feedback}
Platforma: {platform}

Ulepsz zgodnie z uwagami:
- Zachowaj format platformy
- Popraw wskazane elementy
- Wzmocnij przekaz''',
            'Poprawia warianty z feedbackiem'),
            
        'generate_standalone_sm': (1,
            '''Wygeneruj samodzielny post SM.
Platforma: {platform}
Temat: {topic}
Strategia: {communication_strategy}
Typ: {post_type}

Stwórz angażujący post:
- Hook na początku
- Wartościowa treść
- CTA na końcu
- Hashtagi (jeśli platforma)''',
            'Generuje samodzielne posty SM')
    }
    
    # Check and insert/update each prompt
    for prompt_name, (version, template, description) in all_prompts.items():
        # Check if prompt exists
        result = connection.execute(
            text("SELECT id FROM ai_prompts WHERE prompt_name = :name"),
            {"name": prompt_name}
        ).first()
        
        if result is None:
            # Insert new prompt
            connection.execute(
                text("""
                    INSERT INTO ai_prompts (prompt_name, prompt_template, description, version, created_at, updated_at)
                    VALUES (:name, :template, :description, :version, :created_at, :updated_at)
                """),
                {
                    "name": prompt_name,
                    "template": template,
                    "description": description,
                    "version": version,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow()
                }
            )
            print(f"Created prompt: {prompt_name}")
        else:
            # Update existing prompt to ensure it has correct template
            connection.execute(
                text("""
                    UPDATE ai_prompts 
                    SET prompt_template = :template,
                        description = :description,
                        version = :version,
                        updated_at = :updated_at
                    WHERE prompt_name = :name
                """),
                {
                    "name": prompt_name,
                    "template": template,
                    "description": description,
                    "version": version,
                    "updated_at": datetime.utcnow()
                }
            )
            print(f"Updated prompt: {prompt_name}")
    
    print(f"Ensured {len(all_prompts)} AI prompts exist in database")

def downgrade():
    """This migration ensures prompts exist, downgrade does nothing to preserve data"""
    pass  # We don't want to delete prompts on downgrade
