#!/usr/bin/env python
"""Run migration 032 manually to ensure all prompts exist"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ada_user:ada_pass@localhost:5432/ada_db")
engine = create_engine(DATABASE_URL)

all_prompts = {
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

print("Checking and adding missing prompts...")
added_count = 0
updated_count = 0

with engine.connect() as connection:
    # Start transaction
    trans = connection.begin()
    
    try:
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
                print(f"  ✅ Added prompt: {prompt_name}")
                added_count += 1
            else:
                print(f"  ℹ️ Prompt already exists: {prompt_name}")
        
        trans.commit()
        print(f"\n✅ Migration complete! Added {added_count} new prompts.")
        
    except Exception as e:
        trans.rollback()
        print(f"\n❌ Error: {e}")
        sys.exit(1)

# Show final count
with engine.connect() as connection:
    result = connection.execute(text("SELECT COUNT(*) FROM ai_prompts")).scalar()
    print(f"\nTotal prompts in database: {result}")
