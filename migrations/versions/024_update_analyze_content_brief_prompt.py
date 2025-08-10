"""Update analyze_content_brief prompt for better extraction

Revision ID: 024_update_analyze_content_brief_prompt
Revises: 023_add_brief_analysis_prompt
Create Date: 2025-07-28

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '024_update_analyze_content_brief_prompt'
down_revision = '023_add_brief_analysis_prompt'
branch_labels = None
depends_on = None

def upgrade():
    # Update the analyze_content_brief prompt
    op.execute("""
        INSERT INTO ai_prompts (prompt_name, prompt_template, is_active, created_at, updated_at)
        VALUES ('analyze_content_brief', 
'Jesteś ekspertem analizy briefów marketingowych. Przeanalizuj dokładnie poniższy brief i wyodrębnij kluczowe informacje.

Brief Content:
---
{brief_content}
---

INSTRUKCJE ANALIZY:
1. Zidentyfikuj KONKRETNE TEMATY, które brief WYMAGA do zrealizowania (np. "system monitoringu energii", "symulacje CFD")
2. Wyodrębnij DOKŁADNE INSTRUKCJE dotyczące tworzenia treści (np. "2 posty powinny zachęcać do czytania blogów")
3. Znajdź AKTUALNOŚCI FIRMY (nowi pracownicy, projekty, osiągnięcia)
4. Określ KLUCZOWE KOMUNIKATY do przekazania

Zwróć wynik WYŁĄCZNIE w formacie JSON z następującymi polami:
{
  "mandatory_topics": ["Lista KONKRETNYCH tematów, które MUSZĄ być zrealizowane"],
  "content_instructions": ["Lista DOKŁADNYCH instrukcji dotyczących tworzenia treści"],
  "company_news": ["Lista aktualności firmy"],
  "key_messages": ["Lista głównych komunikatów"],
  "key_topics": ["Lista ogólnych tematów/obszarów tematycznych"],
  "important_dates": ["Ważne daty lub terminy"],
  "target_focus": ["Grupy docelowe"],
  "priority_items": ["Priorytety do realizacji"],
  "content_suggestions": ["Sugestie treści"],
  "context_summary": "Krótkie podsumowanie briefu (max 200 słów)"
}

WAŻNE:
- W "mandatory_topics" umieść TYLKO konkretne tematy wymienione w briefie (np. "System monitoringu zużycia energii", "Symulacje CFD w ochronie przeciwpożarowej")
- W "content_instructions" umieść TYLKO konkretne instrukcje (np. "2 posty zachęcające do czytania blogów", "posty o energii dla dużych zakładów")
- NIE dodawaj ogólnych tematów do mandatory_topics - tylko te KONKRETNIE wymienione w briefie', 
        true, NOW(), NOW())
        ON CONFLICT (prompt_name) 
        DO UPDATE SET 
            prompt_template = EXCLUDED.prompt_template,
            updated_at = NOW();
    """)
    
    # Also add model assignment if not exists
    op.execute("""
        INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
        VALUES ('analyze_content_brief', 'gemini-1.5-pro-latest', NOW(), NOW())
        ON CONFLICT (task_name) DO NOTHING;
    """)

def downgrade():
    # Revert to previous prompt
    op.execute("""
        UPDATE ai_prompts 
        SET prompt_template = 'Analyze the following content brief and extract key information:

Brief Content:
---
{brief_content}
---

Please extract and provide in JSON format:
1. "key_topics": List of main topics/themes (max 10)
2. "important_dates": Any mentioned dates or timeframes
3. "key_messages": Core messages to communicate
4. "target_focus": Specific audience or market segments mentioned
5. "priority_items": High-priority items or urgent matters
6. "content_suggestions": Suggested content ideas based on the brief
7. "context_summary": Brief summary of the context (max 200 words)

Respond ONLY with valid JSON.',
        updated_at = NOW()
        WHERE prompt_name = 'analyze_content_brief';
    """)