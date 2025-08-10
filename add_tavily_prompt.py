#!/usr/bin/env python3
"""Add Tavily query generation prompt to database."""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.database import SessionLocal
from app.db import models

def add_tavily_prompt():
    db = SessionLocal()
    try:
        # Check if prompt already exists
        existing = db.query(models.AIPrompt).filter(
            models.AIPrompt.prompt_name == "generate_tavily_queries"
        ).first()
        
        if existing:
            print("Prompt already exists, updating...")
            existing.prompt_template = """Jesteś ekspertem w wyszukiwaniu informacji.

Na podstawie tematu: "{topic}"
Kontekstu branży: "{industry}"
I celu: "{purpose}"

Wygeneruj 3-5 zapytań do wyszukiwarki internetowej, które pomogą znaleźć:
1. Aktualne trendy i nowości w branży związane z tematem
2. Najnowsze regulacje, zmiany prawne lub standardy
3. Przykłady wdrożeń, case studies lub dobre praktyki
4. Statystyki i dane rynkowe
5. Innowacje technologiczne

Zapytania powinny być:
- Konkretne i precyzyjne
- W języku polskim (chyba że branża wymaga terminów angielskich)
- Zróżnicowane (różne aspekty tematu)
- Aktualne (dodaj rok {current_year} gdzie to zasadne)

Zwróć TYLKO listę zapytań w formacie JSON:
["zapytanie 1", "zapytanie 2", "zapytanie 3", ...]"""
            existing.description = "Generuje zapytania do Tavily API dla wzbogacenia kontekstu"
        else:
            print("Creating new prompt...")
            prompt = models.AIPrompt(
                prompt_name="generate_tavily_queries",
                prompt_template="""Jesteś ekspertem w wyszukiwaniu informacji.

Na podstawie tematu: "{topic}"
Kontekstu branży: "{industry}"
I celu: "{purpose}"

Wygeneruj 3-5 zapytań do wyszukiwarki internetowej, które pomogą znaleźć:
1. Aktualne trendy i nowości w branży związane z tematem
2. Najnowsze regulacje, zmiany prawne lub standardy
3. Przykłady wdrożeń, case studies lub dobre praktyki
4. Statystyki i dane rynkowe
5. Innowacje technologiczne

Zapytania powinny być:
- Konkretne i precyzyjne
- W języku polskim (chyba że branża wymaga terminów angielskich)
- Zróżnicowane (różne aspekty tematu)
- Aktualne (dodaj rok {current_year} gdzie to zasadne)

Zwróć TYLKO listę zapytań w formacie JSON:
["zapytanie 1", "zapytanie 2", "zapytanie 3", ...]""",
                description="Generuje zapytania do Tavily API dla wzbogacenia kontekstu"
            )
            db.add(prompt)
        
        # Also check/add model assignment
        existing_model = db.query(models.AIModelAssignment).filter(
            models.AIModelAssignment.task_name == "generate_tavily_queries"
        ).first()
        
        if not existing_model:
            print("Creating model assignment...")
            model_assignment = models.AIModelAssignment(
                task_name="generate_tavily_queries",
                model_name="gemini-1.5-flash",
                description="Model dla generowania zapytań do Tavily API"
            )
            db.add(model_assignment)
        
        db.commit()
        print("Tavily prompt added/updated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    add_tavily_prompt()