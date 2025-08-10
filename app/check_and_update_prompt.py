#!/usr/bin/env python3
"""Check and update the analyze_content_brief prompt"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt

# Get the current prompt
db = SessionLocal()

# Check current prompt
prompt = db.query(AIPrompt).filter(AIPrompt.prompt_name == "analyze_content_brief").first()

if prompt:
    print(f"Current prompt ID: {prompt.id}")
    print(f"Current prompt template:\n{prompt.prompt_template}\n")
    
    # Update with a more restrictive prompt
    new_prompt = """Jesteś asystentem analizującym briefy komunikacyjne. Twoim zadaniem jest WYŁĄCZNIE wyodrębnienie informacji, które FAKTYCZNIE znajdują się w dostarczonym tekście.

ZASADY:
1. Analizuj TYLKO to, co jest napisane w briefie
2. NIE dodawaj własnych interpretacji ani pomysłów
3. NIE halucynuj - jeśli czegoś nie ma w tekście, zostaw puste
4. Szukaj KONKRETNYCH informacji z briefu

Brief do analizy:
{brief_content}

Znajdź i wyodrębnij TYLKO informacje, które są EXPLICITE wymienione w briefie:

Zwróć wynik jako JSON z następującą strukturą:
{{
  "mandatory_topics": [],  // Tematy obowiązkowe TYLKO jeśli są wymienione w briefie
  "content_instructions": [],  // Instrukcje dotyczące treści TYLKO z briefu
  "company_news": [],  // Newsy firmowe TYLKO jeśli są w briefie
  "key_messages": [],  // Kluczowe komunikaty TYLKO z briefu
  "key_topics": [],  // Główne tematy TYLKO wymienione w briefie (np. monitoring energii, symulacje CFD, program SMART)
  "important_dates": [],  // Ważne daty TYLKO jeśli są podane
  "target_focus": [],  // Grupy docelowe TYLKO wymienione w briefie
  "priority_items": [],  // Priorytety TYLKO z briefu
  "content_suggestions": [],  // Sugestie treści TYLKO jeśli są w briefie
  "context_summary": ""  // Krótkie podsumowanie tego co FAKTYCZNIE jest w briefie
}}

WAŻNE: Zwróć TYLKO to co FAKTYCZNIE jest w briefie. Nie dodawaj nic od siebie!"""
    
    prompt.prompt_template = new_prompt
    db.commit()
    print("\nPrompt updated successfully!")
    
    # Also create a test script
    with open("test_updated_prompt.py", "w", encoding="utf-8") as f:
        f.write("""#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief
import base64

# Re-analyze brief with updated prompt
db = SessionLocal()
brief = db.query(ContentBrief).filter(ContentBrief.id == 6).first()

if brief:
    print(f"Re-analyzing brief {brief.id} with updated prompt...")
    
    # Clear current analysis
    brief.ai_analysis = None
    brief.key_topics = []
    db.commit()
    
    # Trigger new analysis
    from app.tasks.brief_analysis import analyze_brief_task
    
    with open(brief.file_path, 'rb') as f:
        file_content_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    result = analyze_brief_task.delay(
        brief_id=brief.id,
        file_content_b64=file_content_b64,
        file_mime_type="application/pdf"
    )
    
    print(f"Task ID: {result.id}")
    print("Check Redis for task status...")

db.close()
""")
else:
    print("Prompt not found, creating new one...")
    new_prompt = AIPrompt(
        prompt_name="analyze_content_brief",
        prompt_template=new_prompt,
        description="Prompt for analyzing content briefs",
        category="content_analysis",
        is_active=True
    )
    db.add(new_prompt)
    db.commit()
    print("New prompt created!")

db.close()