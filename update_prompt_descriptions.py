#!/usr/bin/env python3
"""
Skrypt do aktualizacji opisów promptów w bazie danych
"""
import os
import sys
from sqlalchemy import create_engine, text
from prompt_descriptions import PROMPT_DESCRIPTIONS

# Dodaj ścieżkę do projektu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def update_prompt_descriptions():
    """Aktualizuje opisy promptów w bazie danych"""
    
    # Połączenie z bazą danych
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://ada_user:essa123@localhost/ada_db")
    engine = create_engine(DATABASE_URL)
    
    updated_count = 0
    
    with engine.connect() as conn:
        for prompt_name, description in PROMPT_DESCRIPTIONS.items():
            # Aktualizuj opis dla promptu
            result = conn.execute(
                text("""
                    UPDATE ai_prompts 
                    SET description = :description,
                        updated_at = NOW()
                    WHERE prompt_name = :prompt_name
                """),
                {"prompt_name": prompt_name, "description": description}
            )
            
            if result.rowcount > 0:
                updated_count += 1
                print(f"✓ Zaktualizowano opis dla: {prompt_name}")
            else:
                print(f"⚠ Nie znaleziono promptu: {prompt_name}")
        
        conn.commit()
    
    print(f"\nZaktualizowano {updated_count} promptów")

if __name__ == "__main__":
    update_prompt_descriptions()