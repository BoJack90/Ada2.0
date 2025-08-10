#!/usr/bin/env python3
"""Add schedule_topics prompt to database."""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db import models

def add_schedule_prompt():
    db = SessionLocal()
    try:
        # Check if prompt already exists
        existing = db.query(models.AIPrompt).filter(
            models.AIPrompt.prompt_name == "schedule_topics"
        ).first()
        
        if existing:
            print("Prompt already exists, updating...")
            existing.prompt_template = """Jesteś ekspertem w planowaniu publikacji treści.

Na podstawie listy wariantów treści:
{variants_list}

Oraz preferencji harmonogramu:
{scheduling_preferences}

Zaplanuj harmonogram publikacji dla okresu: {plan_period}

Uwzględnij:
1. Optymalne godziny publikacji dla każdej platformy
2. Równomierne rozłożenie treści w czasie
3. Logiczną kolejność (najpierw blog, potem social media)
4. Odstępy między publikacjami (min. 2 godziny)
5. Dni robocze dla blogów, codziennie dla social media

Zwróć listę JSON z obiektami zawierającymi:
- content_variant_id: ID wariantu do opublikowania
- publication_date: Data i godzina publikacji w formacie "YYYY-MM-DD HH:MM"
- reason: Krótkie uzasadnienie wyboru tej daty/godziny

Przykład:
[
  {{
    "content_variant_id": 123,
    "publication_date": "2024-01-15 09:00",
    "reason": "Poniedziałek rano - optymalna pora na artykuł blogowy"
  }}
]"""
            existing.description = "Generuje harmonogram publikacji treści"
            existing.version = 1
        else:
            print("Creating new prompt...")
            prompt = models.AIPrompt(
                prompt_name="schedule_topics",
                prompt_template="""Jesteś ekspertem w planowaniu publikacji treści.

Na podstawie listy wariantów treści:
{variants_list}

Oraz preferencji harmonogramu:
{scheduling_preferences}

Zaplanuj harmonogram publikacji dla okresu: {plan_period}

Uwzględnij:
1. Optymalne godziny publikacji dla każdej platformy
2. Równomierne rozłożenie treści w czasie
3. Logiczną kolejność (najpierw blog, potem social media)
4. Odstępy między publikacjami (min. 2 godziny)
5. Dni robocze dla blogów, codziennie dla social media

Zwróć listę JSON z obiektami zawierającymi:
- content_variant_id: ID wariantu do opublikowania
- publication_date: Data i godzina publikacji w formacie "YYYY-MM-DD HH:MM"
- reason: Krótkie uzasadnienie wyboru tej daty/godziny

Przykład:
[
  {{
    "content_variant_id": 123,
    "publication_date": "2024-01-15 09:00",
    "reason": "Poniedziałek rano - optymalna pora na artykuł blogowy"
  }}
]""",
                description="Generuje harmonogram publikacji treści",
                version=1
            )
            db.add(prompt)
        
        # Also check/add model assignment
        existing_model = db.query(models.AIModelAssignment).filter(
            models.AIModelAssignment.task_name == "schedule_topics"
        ).first()
        
        if not existing_model:
            print("Creating model assignment...")
            model_assignment = models.AIModelAssignment(
                task_name="schedule_topics",
                model_name="gemini-1.5-flash",
                description="Model dla planowania harmonogramu publikacji"
            )
            db.add(model_assignment)
        
        db.commit()
        print("Schedule prompt added/updated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_schedule_prompt()