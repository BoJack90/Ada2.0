-- Initialize AI prompts and model assignments

-- Insert strategy_parser prompt
INSERT INTO ai_prompts (prompt_name, prompt_template, version, created_at, updated_at)
VALUES ('strategy_parser', 
'Jesteś precyzyjnym systemem do ekstrakcji danych. Twoim zadaniem jest przeanalizowanie załączonego dokumentu strategii komunikacji i wyodrębnienie z niego informacji w ściśle określonym formacie JSON.

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

**Rozpocznij analizę dokumentu:**

{strategy_content}',
1, 
NOW(), 
NOW())
ON CONFLICT (prompt_name) DO UPDATE 
SET prompt_template = EXCLUDED.prompt_template,
    version = EXCLUDED.version,
    updated_at = NOW();

-- Insert model assignment for strategy_parser
INSERT INTO ai_model_assignments (task_name, model_name, created_at, updated_at)
VALUES ('strategy_parser', 'gemini-1.5-pro-latest', NOW(), NOW())
ON CONFLICT (task_name) DO UPDATE 
SET model_name = EXCLUDED.model_name,
    updated_at = NOW();