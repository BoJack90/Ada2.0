#!/usr/bin/env python3
"""Update SM blog context prompt to match code"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt

db = SessionLocal()

# Update the prompt to match what's being passed in main_flow.py
prompt = db.query(AIPrompt).filter(AIPrompt.prompt_name == "generate_sm_variants_from_blog_context").first()

if prompt:
    # Update to match the variables actually passed: sm_posts_per_blog, blog_topic_title, blog_topic_description
    prompt.prompt_template = """Jesteś ekspertem social media tworzącym angażujące posty.

Na podstawie poniższego tematu blogowego, wygeneruj {sm_posts_per_blog} postów na social media.

TEMAT BLOGOWY:
Tytuł: {blog_topic_title}
Opis: {blog_topic_description}

Wygeneruj {sm_posts_per_blog} różnorodnych postów, które:
1. Nawiązują do tematu blogowego ale prezentują go z różnych perspektyw
2. Są krótkie i angażujące (odpowiednie dla social media)
3. Zawierają elementy przyciągające uwagę (pytania, ciekawostki, statystyki)
4. Używają odpowiednich hashtagów
5. Zachęcają do przeczytania pełnego artykułu
6. Są zróżnicowane w formie (pytanie, porada, ciekawostka, cytat)

Zwróć wynik jako JSON w formacie:
[
  {{
    "title": "Tytuł/temat posta SM",
    "description": "Pełna treść posta",
    "platform_suggestion": "LinkedIn/Facebook/Twitter",
    "hashtags": "#automatyka #bezpieczeństwo #technologia"
  }}
]

WAŻNE: Zwróć dokładnie {sm_posts_per_blog} postów w formacie JSON."""
    
    db.commit()
    print("Updated prompt template successfully!")
    print(f"New template uses variables: sm_posts_per_blog, blog_topic_title, blog_topic_description")
else:
    print("Prompt not found!")

db.close()