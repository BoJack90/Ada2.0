#!/usr/bin/env python3
"""Update analyze_content_brief prompt to better extract employee info"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt

db = SessionLocal()

prompt = db.query(AIPrompt).filter(AIPrompt.prompt_name == "analyze_content_brief").first()

if prompt:
    prompt.prompt_template = """Jesteś asystentem analizującym briefy komunikacyjne. Twoim zadaniem jest WYŁĄCZNIE wyodrębnienie informacji, które FAKTYCZNIE znajdują się w dostarczonym tekście.

ZASADY:
1. Analizuj TYLKO to, co jest napisane w briefie
2. NIE dodawaj własnych interpretacji ani pomysłów
3. NIE halucynuj - jeśli czegoś nie ma w tekście, zostaw puste
4. Szukaj KONKRETNYCH informacji z briefu
5. SZCZEGÓLNIE zwróć uwagę na informacje o nowych pracownikach (np. "Dołączyła do nas...")

Brief do analizy:
{brief_content}

Znajdź i wyodrębnij TYLKO informacje, które są EXPLICITE wymienione w briefie:

Zwróć wynik jako JSON z następującą strukturą:
{{
  "mandatory_topics": [],  // Tematy obowiązkowe TYLKO jeśli są wymienione w briefie
  "content_instructions": [],  // Instrukcje dotyczące treści TYLKO z briefu
  "company_news": [],  // Newsy firmowe - UWAGA: jeśli jest "Dołączyła/Dołączył do nas [Imię Nazwisko]", dodaj jako osobny element!
  "key_messages": [],  // Kluczowe komunikaty TYLKO z briefu
  "key_topics": [],  // Główne tematy TYLKO wymienione w briefie
  "important_dates": [],  // Ważne daty TYLKO jeśli są podane
  "target_focus": [],  // Grupy docelowe TYLKO wymienione w briefie
  "priority_items": [],  // Priorytety TYLKO z briefu
  "content_suggestions": [],  // Sugestie treści TYLKO jeśli są w briefie
  "context_summary": ""  // Krótkie podsumowanie tego co FAKTYCZNIE jest w briefie
}}

PRZYKŁAD: Jeśli w briefie jest "Dołączyła do nas Natalia Szarach... Stanowisko: Manager ds. efektywności operacyjnej", 
to w company_news powinno być: "Dołączyła do nas Natalia Szarach - nowy Manager ds. efektywności operacyjnej i analiz"

WAŻNE: Zwróć TYLKO to co FAKTYCZNIE jest w briefie. Nie dodawaj nic od siebie!"""
    
    db.commit()
    print("✓ Zaktualizowano prompt 'analyze_content_brief'")
    print("Prompt teraz lepiej wyodrębnia informacje o nowych pracownikach")
else:
    print("❌ Nie znaleziono promptu")

db.close()