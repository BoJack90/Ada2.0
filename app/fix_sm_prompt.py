#!/usr/bin/env python3
"""Create missing SM generation prompt"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt

# Check existing prompts
db = SessionLocal()

# Check if prompt exists
existing = db.query(AIPrompt).filter(AIPrompt.prompt_name == "generate_sm_variants_from_blog_context").first()

if existing:
    print(f"Prompt already exists with ID: {existing.id}")
else:
    # Create the missing prompt
    new_prompt = AIPrompt(
        prompt_name="generate_sm_variants_from_blog_context",
        prompt_template="""Jesteś ekspertem social media w firmie {organization_name} ({organization_industry}).

Na podstawie poniższego tematu blogowego, wygeneruj {post_count} angażujących postów na platformę {platform_name}.

TEMAT BLOGOWY:
Tytuł: {blog_title}
Opis: {blog_description}

WYMAGANIA DLA PLATFORMY {platform_name}:
{platform_requirements}

STYL KOMUNIKACJI:
{general_style}

DODATKOWE INFORMACJE:
{brief_insights}

Wygeneruj {post_count} różnorodnych postów, które:
1. Nawiązują do tematu blogowego ale prezentują go z różnych perspektyw
2. Są dopasowane do charakteru platformy {platform_name}
3. Zawierają elementy angażujące (pytania, fakty, porady)
4. Używają odpowiednich hashtagów
5. Mają odpowiednią długość dla platformy

Zwróć wynik jako JSON w formacie:
[
  {{
    "content": "Treść posta",
    "hashtags": ["hashtag1", "hashtag2"],
    "cta": "Wezwanie do działania",
    "tone": "ton komunikacji (profesjonalny/casualowy/edukacyjny)"
  }}
]""",
        description="Prompt for generating social media posts based on blog topics"
    )
    db.add(new_prompt)
    db.commit()
    print(f"Created new prompt with ID: {new_prompt.id}")

# Also check for other potentially missing SM prompts
sm_prompts = [
    "generate_sm_from_brief",
    "generate_standalone_sm_posts"
]

for prompt_name in sm_prompts:
    exists = db.query(AIPrompt).filter(AIPrompt.prompt_name == prompt_name).first()
    if not exists:
        print(f"WARNING: Prompt '{prompt_name}' is also missing!")

db.close()