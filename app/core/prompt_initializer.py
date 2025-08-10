"""
System inicjalizacji podstawowych promptów AI.
Automatycznie ładuje prompty przy starcie aplikacji.
"""

from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from datetime import datetime
from app.db.models import AIPrompt, AIModelAssignment
from app.db.database import SessionLocal


class PromptInitializer:
    """Klasa odpowiedzialna za inicjalizację podstawowych promptów AI"""
    
    @staticmethod
    def get_default_prompts() -> Dict[str, Dict[str, any]]:
        """Zwraca słownik wszystkich podstawowych promptów systemowych"""
        return {
            "strategy_parser": {
                "template": """Jesteś ekspertem w analizie dokumentów strategii komunikacji. Przeanalizuj poniższy dokument i wyodrębnij wszystkie kluczowe informacje.

WAŻNE: Zwróć TYLKO czysty JSON bez żadnych dodatkowych komentarzy, markdown czy formatowania.

Dokument do analizy:
{strategy_content}

Zwróć dane w następującym formacie JSON:
{
  "name": "nazwa strategii komunikacji",
  "description": "szczegółowy opis strategii",
  "communication_goals": ["cel komunikacyjny 1", "cel komunikacyjny 2"],
  "target_audiences": [
    {"name": "nazwa grupy docelowej", "description": "szczegółowy opis grupy"}
  ],
  "general_style": {
    "language": "język komunikacji (np. polski)",
    "tone": "ton komunikacji (np. profesjonalny, przyjazny)",
    "technical_content": "sposób prezentacji treści technicznych",
    "employer_branding_content": "sposób prezentacji employer brandingu"
  },
  "platform_styles": [
    {
      "platform_name": "nazwa platformy (np. LinkedIn)",
      "length_description": "opis długości postów",
      "style_description": "opis stylu komunikacji",
      "notes": "dodatkowe uwagi"
    }
  ],
  "forbidden_phrases": ["zakazana fraza 1", "zakazana fraza 2"],
  "preferred_phrases": ["preferowana fraza 1", "preferowana fraza 2"],
  "cta_rules": [
    {"content_type": "typ treści", "cta_text": "tekst CTA"}
  ],
  "sample_content_types": ["post LinkedIn", "artykuł blogowy"]
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "generate_blog_topics_for_selection": {
                "template": """Jesteś ekspertem content marketingu. Na podstawie analizy briefu komunikacyjnego, wygeneruj {topics_count} propozycji tematów blogowych.

Analiza briefu:
{brief_analysis}

Strategia komunikacji:
{strategy_info}

WAŻNE WYTYCZNE:
1. Każdy temat musi być unikalny i wartościowy dla grupy docelowej
2. Tematy powinny wspierać cele komunikacyjne marki
3. Uwzględnij SEO i potencjał organicznego ruchu
4. Tematy powinny być aktualne i angażujące

Zwróć TYLKO czysty JSON w formacie:
{
  "topics": [
    {
      "title": "tytuł artykułu",
      "description": "krótki opis tematu (2-3 zdania)",
      "target_audience": "główna grupa docelowa",
      "keywords": ["słowo kluczowe 1", "słowo kluczowe 2"],
      "content_pillar": "filar tematyczny",
      "estimated_impact": "wysoki/średni/niski"
    }
  ]
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "generate_content_plan": {
                "template": """Stwórz szczegółowy plan treści na podstawie wybranego tematu i strategii komunikacji.

Temat: {topic_title}
Opis tematu: {topic_description}
Grupa docelowa: {target_audience}
Strategia: {strategy_info}

Zwróć plan w formacie JSON:
{
  "main_topic": "główny temat",
  "content_structure": {
    "introduction": "opis wstępu",
    "main_points": ["punkt 1", "punkt 2", "punkt 3"],
    "conclusion": "opis zakończenia"
  },
  "key_messages": ["kluczowy przekaz 1", "kluczowy przekaz 2"],
  "cta_suggestions": ["propozycja CTA 1", "propozycja CTA 2"],
  "content_length": "sugerowana długość",
  "tone_guidelines": "wytyczne dotyczące tonu"
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "generate_blog_content": {
                "template": """Napisz profesjonalny artykuł blogowy na podstawie planu treści.

Plan treści:
{content_plan}

Strategia komunikacji:
{strategy_info}

Dodatkowe wytyczne:
- Długość: {content_length} słów
- Ton: {tone}
- Grupa docelowa: {target_audience}

WAŻNE: Artykuł powinien być wartościowy, angażujący i zgodny ze strategią marki.

Zwróć artykuł w formacie JSON:
{
  "title": "tytuł artykułu",
  "meta_description": "meta opis (max 160 znaków)",
  "content": "pełna treść artykułu w formacie HTML",
  "excerpt": "zajawka (max 200 znaków)",
  "tags": ["tag1", "tag2", "tag3"],
  "internal_links_suggestions": ["sugestia linku 1", "sugestia linku 2"]
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "generate_social_media_variant": {
                "template": """Stwórz wariant posta na social media na podstawie artykułu blogowego.

Platforma: {platform}
Artykuł źródłowy:
Tytuł: {article_title}
Treść: {article_content}

Wytyczne dla platformy {platform}:
{platform_guidelines}

Zwróć post w formacie JSON:
{
  "content": "treść posta",
  "hashtags": ["#hashtag1", "#hashtag2"],
  "cta": "call to action",
  "visual_suggestions": "sugestie dotyczące grafiki",
  "best_posting_time": "sugerowany czas publikacji",
  "engagement_tips": ["wskazówka 1", "wskazówka 2"]
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "analyze_content_brief": {
                "template": """Przeanalizuj brief komunikacyjny i wyodrębnij kluczowe informacje.

Brief:
{brief_content}

Zwróć analizę w formacie JSON:
{
  "key_topics": ["temat 1", "temat 2"],
  "important_dates": ["data 1", "data 2"],
  "key_messages": ["przekaz 1", "przekaz 2"],
  "target_focus": ["fokus 1", "fokus 2"],
  "priority_items": ["priorytet 1", "priorytet 2"],
  "content_suggestions": [
    {
      "type": "typ treści",
      "topic": "temat",
      "urgency": "wysoka/średnia/niska"
    }
  ]
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "revise_content_variant": {
                "template": """Zrewiduj i popraw wariant treści według wskazówek.

Obecna treść:
{current_content}

Wskazówki do rewizji:
{revision_guidelines}

Platforma: {platform}
Strategia: {strategy_info}

Zwróć poprawioną wersję w formacie JSON:
{
  "revised_content": "poprawiona treść",
  "changes_made": ["zmiana 1", "zmiana 2"],
  "improvement_rationale": "uzasadnienie zmian",
  "quality_score": "ocena jakości (1-10)",
  "further_suggestions": ["sugestia 1", "sugestia 2"]
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            },
            
            "contextualize_content": {
                "template": """Dostosuj treść do konkretnego kontekstu i platformy.

Treść źródłowa:
{source_content}

Kontekst:
- Platforma: {platform}
- Cel: {goal}
- Grupa docelowa: {target_audience}
- Ograniczenia: {constraints}

Zwróć dostosowaną treść w formacie JSON:
{
  "contextualized_content": "dostosowana treść",
  "adaptations_made": ["adaptacja 1", "adaptacja 2"],
  "platform_optimization": "optymalizacje dla platformy",
  "expected_performance": "przewidywana skuteczność"
}""",
                "model": "gemini-1.5-pro-latest",
                "version": 1
            }
        }
    
    @staticmethod
    def get_default_model_assignments() -> Dict[str, str]:
        """Zwraca domyślne przypisania modeli do zadań"""
        return {
            "strategy_parser": "gemini-1.5-pro-latest",
            "generate_blog_topics_for_selection": "gemini-1.5-pro-latest",
            "generate_content_plan": "gemini-1.5-pro-latest",
            "generate_blog_content": "gemini-1.5-pro-latest",
            "generate_social_media_variant": "gemini-1.5-pro-latest",
            "analyze_content_brief": "gemini-1.5-pro-latest",
            "revise_content_variant": "gemini-1.5-pro-latest",
            "contextualize_content": "gemini-1.5-pro-latest"
        }
    
    @staticmethod
    def initialize_prompts(db: Session, force: bool = False) -> Dict[str, str]:
        """
        Inicjalizuje podstawowe prompty w bazie danych.
        
        Args:
            db: Sesja bazy danych
            force: Czy nadpisać istniejące prompty
            
        Returns:
            Dict z informacjami o zainicjalizowanych promptach
        """
        results = {
            "created": [],
            "updated": [],
            "skipped": []
        }
        
        default_prompts = PromptInitializer.get_default_prompts()
        
        for prompt_name, prompt_data in default_prompts.items():
            existing_prompt = db.query(AIPrompt).filter(
                AIPrompt.prompt_name == prompt_name
            ).first()
            
            if existing_prompt and not force:
                results["skipped"].append(prompt_name)
            elif existing_prompt and force:
                # Aktualizuj istniejący prompt
                existing_prompt.prompt_template = prompt_data["template"]
                existing_prompt.version = prompt_data["version"]
                existing_prompt.updated_at = datetime.utcnow()
                results["updated"].append(prompt_name)
            else:
                # Stwórz nowy prompt
                new_prompt = AIPrompt(
                    prompt_name=prompt_name,
                    prompt_template=prompt_data["template"],
                    version=prompt_data["version"],
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_prompt)
                results["created"].append(prompt_name)
        
        # Inicjalizuj przypisania modeli
        model_assignments = PromptInitializer.get_default_model_assignments()
        
        for task_name, model_name in model_assignments.items():
            existing_assignment = db.query(AIModelAssignment).filter(
                AIModelAssignment.task_name == task_name
            ).first()
            
            if not existing_assignment:
                new_assignment = AIModelAssignment(
                    task_name=task_name,
                    model_name=model_name,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(new_assignment)
        
        db.commit()
        return results
    
    @staticmethod
    def check_and_initialize():
        """Sprawdza i inicjalizuje prompty przy starcie aplikacji"""
        db = SessionLocal()
        try:
            # Sprawdź czy są jakiekolwiek prompty
            prompt_count = db.query(AIPrompt).count()
            
            if prompt_count == 0:
                print("No AI prompts found. Initializing default prompts...")
                results = PromptInitializer.initialize_prompts(db)
                print(f"Prompts initialization results: {results}")
            else:
                print(f"Found {prompt_count} existing prompts.")
                
                # Sprawdź czy wszystkie wymagane prompty istnieją
                required_prompts = PromptInitializer.get_default_prompts().keys()
                existing_prompts = {p.prompt_name for p in db.query(AIPrompt).all()}
                missing_prompts = set(required_prompts) - existing_prompts
                
                if missing_prompts:
                    print(f"Missing prompts: {missing_prompts}")
                    # Inicjalizuj tylko brakujące
                    for prompt_name in missing_prompts:
                        prompt_data = PromptInitializer.get_default_prompts()[prompt_name]
                        new_prompt = AIPrompt(
                            prompt_name=prompt_name,
                            prompt_template=prompt_data["template"],
                            version=prompt_data["version"],
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(new_prompt)
                    db.commit()
                    print(f"Added {len(missing_prompts)} missing prompts.")
                    
        finally:
            db.close()