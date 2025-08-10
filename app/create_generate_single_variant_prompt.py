#!/usr/bin/env python3
"""Create generate_single_variant prompt"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import AIPrompt, AIModelAssignment

db = SessionLocal()

# Create generate_single_variant prompt
existing = db.query(AIPrompt).filter(AIPrompt.prompt_name == "generate_single_variant").first()
if not existing:
    prompt = AIPrompt(
        prompt_name="generate_single_variant",
        prompt_template="""Jesteś ekspertem content marketingu tworzącym treści dla platformy {platform_name}.

TEMAT DO OPRACOWANIA:
Tytuł: {topic_title}
Opis: {topic_description}

KONTEKST STRATEGII KOMUNIKACJI:
{general_strategy_context}

SZCZEGÓŁOWE ZASADY DLA PLATFORMY {platform_name}:
{platform_rules}

Stwórz angażującą treść, która:
1. Jest zgodna ze strategią komunikacji firmy
2. Respektuje zasady i ograniczenia platformy
3. Wykorzystuje odpowiedni ton i styl komunikacji
4. Zawiera wartościowe informacje dla odbiorców
5. Ma odpowiednią długość dla platformy
6. Zawiera elementy angażujące (pytania, ciekawostki, porady)
7. Kończy się wezwaniem do działania (CTA)

Format odpowiedzi - zwróć TYLKO treść posta, bez dodatkowych komentarzy czy wyjaśnień.""",
        description="Prompt for generating single content variant"
    )
    db.add(prompt)
    db.commit()
    print(f"Created prompt 'generate_single_variant' with ID: {prompt.id}")
else:
    print("Prompt 'generate_single_variant' already exists")

# Create model assignment
existing_assignment = db.query(AIModelAssignment).filter(
    AIModelAssignment.task_name == "generate_single_variant"
).first()

if not existing_assignment:
    assignment = AIModelAssignment(
        task_name="generate_single_variant",
        model_name="models/gemini-1.5-pro-latest",
        description="Generate single content variant for platform"
    )
    db.add(assignment)
    db.commit()
    print("Created model assignment for 'generate_single_variant'")
else:
    print("Model assignment for 'generate_single_variant' already exists")

# Also create regenerate_single_variant prompt (mentioned in the code)
existing_regen = db.query(AIPrompt).filter(AIPrompt.prompt_name == "regenerate_single_variant").first()
if not existing_regen:
    regen_prompt = AIPrompt(
        prompt_name="regenerate_single_variant",
        prompt_template="""Jesteś ekspertem content marketingu. Przeanalizuj poprzednią wersję treści i stwórz nową, ulepszoną wersję.

TEMAT DO OPRACOWANIA:
Tytuł: {topic_title}
Opis: {topic_description}

KONTEKST STRATEGII KOMUNIKACJI:
{general_strategy_context}

SZCZEGÓŁOWE ZASADY DLA PLATFORMY {platform_name}:
{platform_rules}

Stwórz NOWĄ wersję treści, która:
1. Jest bardziej angażująca niż poprzednia
2. Wykorzystuje inne podejście do tematu
3. Zachowuje zgodność ze strategią komunikacji
4. Jest świeża i oryginalna
5. Zawiera wartościowe informacje
6. Ma elementy wyróżniające (statystyki, ciekawostki, przykłady)

Format odpowiedzi - zwróć TYLKO treść posta, bez dodatkowych komentarzy.""",
        description="Prompt for regenerating content variant"
    )
    db.add(regen_prompt)
    db.commit()
    print(f"Created prompt 'regenerate_single_variant' with ID: {regen_prompt.id}")

# Create model assignment for regenerate
existing_regen_assignment = db.query(AIModelAssignment).filter(
    AIModelAssignment.task_name == "regenerate_single_variant"
).first()

if not existing_regen_assignment:
    regen_assignment = AIModelAssignment(
        task_name="regenerate_single_variant",
        model_name="models/gemini-1.5-pro-latest",
        description="Regenerate content variant for platform"
    )
    db.add(regen_assignment)
    db.commit()
    print("Created model assignment for 'regenerate_single_variant'")

db.close()
print("\nAll variant generation prompts created!")