"""update_strategy_parser_prompt

Revision ID: 003
Revises: 002
Create Date: 2025-01-10 15:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Update the strategy_parser prompt to advanced version"""
    
    # Advanced prompt template for strategy parsing
    advanced_prompt = """Jesteś precyzyjnym systemem do ekstrakcji danych. Twoim zadaniem jest przeanalizowanie załączonego dokumentu strategii komunikacji i wyodrębnienie z niego informacji w ściśle określonym formacie JSON.

**Kluczowa zasada: Jeśli jakaś sekcja (np. "Zabronione frazy") nie występuje w dokumencie, zwróć dla odpowiadającego jej pola w JSON pustą listę `[]` lub wartość `null`. Nie wymyślaj informacji.**

Musisz zwrócić **WYŁĄCZNIE** validny obiekt JSON, który jest zgodny z poniższym schematem. Nie dodawaj żadnych wyjaśnień ani formatowania markdown przed lub po obiekcie JSON.

Schemat JSON:
{json_schema}

**Instrukcje analizy:**
1. Przeanalizuj dokument w poszukiwaniu informacji o strategii komunikacji
2. Wyodrębnij cele komunikacyjne (communication_goals)
3. Zidentyfikuj grupy docelowe jako persony (target_audiences)
4. Znajdź informacje o ogólnym stylu komunikacji (general_style)
5. Wyszukaj style dla konkretnych platform (platform_styles)
6. Zidentyfikuj zakazane frazy (forbidden_phrases)
7. Znajdź preferowane zwroty (preferred_phrases)
8. Wyodrębnij reguły CTA (cta_rules)
9. Zidentyfikuj przykładowe typy treści (sample_content_types)

**Ważne:** Jeśli jakaś informacja nie jest dostępna w dokumencie, użyj wartości `null` lub pustej listy `[]`.

**Przykład odpowiedzi JSON:**
```json
{
    "name": "Strategia komunikacji firmy XYZ",
    "description": "Strategia komunikacji marketingowej...",
    "communication_goals": [
        "Zwiększenie świadomości marki",
        "Pozyskanie nowych klientów"
    ],
    "target_audiences": [
        {
            "name": "Młodzi profesjonaliści",
            "description": "Osoby w wieku 25-35 lat z wykształceniem wyższym"
        }
    ],
    "general_style": {
        "language": "polski",
        "tone": "profesjonalny i przyjazny",
        "technical_content": "Upraszczanie terminów technicznych",
        "employer_branding_content": "Eksponowanie wartości firmy"
    },
    "platform_styles": [
        {
            "platform_name": "LinkedIn",
            "length_description": "Posty 100-200 słów",
            "style_description": "Profesjonalny, ekspertowy",
            "notes": "Używanie hashtagów branżowych"
        }
    ],
    "forbidden_phrases": ["sprzedaż agresywna", "błyskawiczny zysk"],
    "preferred_phrases": ["wartość dodana", "rozwiązanie biznesowe"],
    "cta_rules": [
        {
            "content_type": "post LinkedIn",
            "cta_text": "Skontaktuj się z nami"
        }
    ],
    "sample_content_types": ["post LinkedIn", "artykuł blogowy", "newsletter"]
}
```

**Rozpocznij analizę dokumentu:**

{strategy_content}"""
    
    # Update the prompt template
    now = datetime.utcnow()
    
    # Use SQL with escaped quotes for the prompt template
    sql_update = f"""
    UPDATE ai_prompts 
    SET prompt_template = '{advanced_prompt.replace("'", "''")}',
        version = version + 1,
        updated_at = '{now}'
    WHERE prompt_name = 'strategy_parser'
    """
    
    op.execute(sql_update)


def downgrade():
    """Revert to the original simple prompt"""
    
    # Original simple prompt
    simple_prompt = """Analizuj strategię: {strategy_text}"""
    
    # Revert the prompt template
    now = datetime.utcnow()
    
    # Use SQL with escaped quotes for the prompt template
    sql_update = f"""
    UPDATE ai_prompts 
    SET prompt_template = '{simple_prompt.replace("'", "''")}',
        version = 1,
        updated_at = '{now}'
    WHERE prompt_name = 'strategy_parser'
    """
    
    op.execute(sql_update) 