#!/usr/bin/env python3
"""Update generate_sm_from_brief prompt to include company news"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt

db = SessionLocal()

# Update the prompt
prompt = db.query(AIPrompt).filter(AIPrompt.prompt_name == "generate_sm_from_brief").first()

if prompt:
    prompt.prompt_template = """Jesteś ekspertem social media w firmie Akson Elektro.

Na podstawie poniższych informacji z briefu komunikacyjnego, wygeneruj {count} angażujących postów na social media.

AKTUALNOŚCI FIRMOWE:
{company_news}

FRAGMENTY Z BRIEFU:
{brief_excerpts}

KLUCZOWE TEMATY:
{key_topics}

PRIORYTETY:
{priority_items}

SUGESTIE TREŚCI:
{content_suggestions}

ZADANIE:
Wygeneruj {count} różnorodnych postów na social media, które:
1. Wykorzystują KONKRETNE informacje z briefu (np. o nowych pracownikach, projektach, wydarzeniach)
2. Są napisane w przyjaznym, ale profesjonalnym tonie
3. Angażują odbiorców (pytania, gratulacje, ciekawostki)
4. Promują życie firmy i jej wartości
5. Są odpowiednie dla platform LinkedIn i Facebook

WAŻNE: Jeśli w briefie jest informacja o nowym pracowniku (np. "Dołączyła do nas Natalia Szarach"), KONIECZNIE napisz post powitalny!

Zwróć wynik jako JSON:
[
  {{
    "title": "Tytuł/temat posta",
    "description": "Pełna treść posta (150-300 znaków)",
    "platform": "LinkedIn/Facebook",
    "hashtags": "#NowyPracownik #TeamAkson #WelcomeToTeam"
  }}
]"""
    
    db.commit()
    print("✓ Zaktualizowano prompt 'generate_sm_from_brief'")
    print("Prompt teraz używa:")
    print("- company_news (aktualności firmowe)")
    print("- brief_excerpts (fragmenty briefu)")
    print("- key_topics, priority_items, content_suggestions")
else:
    print("❌ Nie znaleziono promptu 'generate_sm_from_brief'")

db.close()