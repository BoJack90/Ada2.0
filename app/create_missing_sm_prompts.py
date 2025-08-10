#!/usr/bin/env python3
"""Create all missing SM generation prompts"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt

db = SessionLocal()

# Define missing prompts
missing_prompts = [
    {
        "prompt_name": "generate_sm_from_brief",
        "prompt_template": """Jesteś ekspertem social media w firmie {organization_name}.

Na podstawie poniższych informacji z briefu komunikacyjnego, wygeneruj {count} postów na social media.

INFORMACJE Z BRIEFU:
Kluczowe tematy: {key_topics}
Priorytety: {priority_items}
Sugestie treści: {content_suggestions}
Aktualności firmowe: {company_news}

STYL KOMUNIKACJI:
{general_style}

Wygeneruj {count} angażujących postów, które:
1. Odnoszą się do tematów z briefu
2. Wykorzystują aktualności firmowe
3. Są zróżnicowane pod względem formy i treści
4. Zawierają odpowiednie hashtagi
5. Mają wezwania do działania

Zwróć wynik jako JSON:
[
  {{
    "title": "Tytuł/temat posta",
    "content": "Pełna treść posta",
    "platform": "sugerowana platforma",
    "hashtags": ["hashtag1", "hashtag2"],
    "cta": "Wezwanie do działania"
  }}
]""",
        "description": "Prompt for generating SM posts based on brief insights"
    },
    {
        "prompt_name": "generate_standalone_sm_posts",
        "prompt_template": """Jesteś ekspertem social media w firmie {organization_name} z branży {organization_industry}.

Wygeneruj {count} samodzielnych postów na social media, które nie są powiązane z konkretnymi wpisami blogowymi.

STRATEGIA KOMUNIKACJI:
{communication_strategy}

STYL OGÓLNY:
{general_style}

ODRZUCONE TEMATY (NIE UŻYWAJ):
{rejected_topics}

Stwórz {count} różnorodnych postów, które:
1. Prezentują firmę jako eksperta w branży
2. Budują zaangażowanie społeczności
3. Edukują i inspirują odbiorców
4. Są dopasowane do różnych platform SM
5. Wykorzystują trendy branżowe

Zwróć wynik jako JSON:
[
  {{
    "title": "Tytuł/temat posta",
    "content": "Pełna treść posta",
    "platform": "sugerowana platforma",
    "hashtags": ["hashtag1", "hashtag2"],
    "tone": "ton komunikacji",
    "category": "kategoria (edukacja/inspiracja/news/porada)"
  }}
]""",
        "description": "Prompt for generating standalone SM posts"
    }
]

# Create missing prompts
for prompt_data in missing_prompts:
    existing = db.query(AIPrompt).filter(AIPrompt.prompt_name == prompt_data["prompt_name"]).first()
    if not existing:
        new_prompt = AIPrompt(
            prompt_name=prompt_data["prompt_name"],
            prompt_template=prompt_data["prompt_template"],
            description=prompt_data["description"]
        )
        db.add(new_prompt)
        db.commit()
        print(f"Created prompt '{prompt_data['prompt_name']}' with ID: {new_prompt.id}")
    else:
        print(f"Prompt '{prompt_data['prompt_name']}' already exists")

# Also create AI model assignments if needed
from app.db.models import AIModelAssignment

sm_tasks = [
    ("generate_sm_variants_from_blog_context", "Generate SM posts from blog topics"),
    ("generate_sm_from_brief", "Generate SM posts from brief insights"),
    ("generate_standalone_sm_posts", "Generate standalone SM posts")
]

for task_name, description in sm_tasks:
    existing = db.query(AIModelAssignment).filter(AIModelAssignment.task_name == task_name).first()
    if not existing:
        assignment = AIModelAssignment(
            task_name=task_name,
            model_name="models/gemini-1.5-pro-latest",
            description=description
        )
        db.add(assignment)
        db.commit()
        print(f"Created model assignment for '{task_name}'")

db.close()
print("\nAll SM prompts and model assignments created!")