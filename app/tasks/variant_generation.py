import logging
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import locale

from sqlalchemy.orm import Session, joinedload
from celery import current_app

from app.tasks.celery_app import celery_app
from app.db.database import get_db
from app.db.models import (
    SuggestedTopic, 
    ContentDraft, 
    ContentVariant, 
    CommunicationStrategy,
    PlatformStyle,
    GeneralStyle,
    AIPrompt,
    AIModelAssignment
)
from app.core.platform_mapping import should_generate_for_platform
from app.core.context_cache import get_cached_context, set_cached_context
# from app.core.external_integrations import ContentResearchOrchestrator  # DISABLED - using existing research from super_context
# Google AI SDK
try:
    import google.generativeai as genai
    import os
    GEMINI_API_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_API_AVAILABLE = False

logger = logging.getLogger(__name__)


def get_temporal_context() -> str:
    """
    Generuje kontekst czasowy dla AI
    """
    now = datetime.now()
    
    # Polish month names
    polish_months = {
        1: "styczeń", 2: "luty", 3: "marzec", 4: "kwiecień",
        5: "maj", 6: "czerwiec", 7: "lipiec", 8: "sierpień",
        9: "wrzesień", 10: "październik", 11: "listopad", 12: "grudzień"
    }
    
    # Determine season
    month = now.month
    if month in [12, 1, 2]:
        season = "zima"
        season_context = "okres zimowy, święta (jeśli grudzień), początek roku (jeśli styczeń/luty)"
    elif month in [3, 4, 5]:
        season = "wiosna"
        season_context = "okres wiosenny, odnawianie, świeże początki"
    elif month in [6, 7, 8]:
        season = "lato"
        season_context = "okres letni, wakacje, urlopy, wysokie temperatury"
    else:  # 9, 10, 11
        season = "jesień"
        season_context = "okres jesienny, powrót do pracy/szkoły, przygotowania do zimy"
    
    # Special context for specific months
    special_context = ""
    if month == 8:
        special_context = "Sierpień - szczyt sezonu urlopowego, wiele osób na wakacjach, przygotowania do września"
    elif month == 9:
        special_context = "Wrzesień - powrót do szkoły/pracy, koniec wakacji, nowy rok szkolny"
    elif month == 12:
        special_context = "Grudzień - okres przedświąteczny, podsumowania roku, plany na nowy rok"
    elif month == 1:
        special_context = "Styczeń - nowy rok, postanowienia noworoczne, świeże starty"
    
    temporal_context = f"""
=== KONTEKST CZASOWY (TYLKO DLA TWOJEJ WIEDZY - NIE WSPOMINAJ WPROST) ===
Data: {now.day} {polish_months[month]} {now.year}
Pora roku: {season}
{special_context}

INSTRUKCJE:
- NIE wspominaj wprost o porze roku w każdym poście (np. "lato w pełni", "zimowa aura")
- NIE pisz o wydarzeniach nieaktualnych (np. Boże Narodzenie w sierpniu, Nowy Rok w lipcu)
- Używaj tego kontekstu TYLKO aby uniknąć nieodpowiednich tematów
- Wspominaj o porze roku TYLKO gdy jest to naturalnie związane z tematem
- Większość postów powinna być uniwersalna, niezależna od pory roku
- Używaj aktualnego roku ({now.year}) gdy to konieczne
"""
    
    return temporal_context


def get_general_strategy_context(communication_strategy: CommunicationStrategy, content_plan_id: int = None, db: Session = None, platform_name: Optional[str] = None, content_type: Optional[str] = None) -> str:
    """
    Buduje kontekst ogólnej strategii klienta na podstawie danych z bazy
    
    Args:
        communication_strategy: Strategia komunikacji organizacji
        content_plan_id: ID planu treści (opcjonalne)
        db: Sesja bazy danych (opcjonalne) 
        platform_name: Nazwa platformy dla selektywnego kontekstu (opcjonalne)
        content_type: Typ treści (blog/social_media) dla selektywnego kontekstu (opcjonalne)
        
    Returns:
        str: Sformatowany kontekst strategii
    """
    # Określ czy to blog czy social media
    is_blog_content = content_type == "blog" or (platform_name and platform_name.lower() == "blog")
    is_social_media = not is_blog_content
    
    # Sprawdź cache z uwzględnieniem typu treści
    cache_key = ["strategy_context", communication_strategy.id, content_type or "general"]
    cached_context = get_cached_context(cache_key)
    if cached_context:
        logger.info(f"Using cached strategy context for strategy {communication_strategy.id} and type {content_type}")
        return cached_context["context"]
    
    context_parts = []
    
    # Pobierz analizę strony internetowej jeśli dostępna
    if db and communication_strategy.organization_id:
        from app.tasks.website_analysis import get_website_analysis_for_organization
        website_analysis = get_website_analysis_for_organization(db, communication_strategy.organization_id)
        
        if website_analysis:
            context_parts.append("=== ANALIZA STRONY INTERNETOWEJ FIRMY ===")
            
            if website_analysis.get('industry'):
                context_parts.append(f"Branża: {website_analysis['industry']}")
            
            if website_analysis.get('services'):
                context_parts.append("Oferowane usługi:")
                for service in website_analysis['services'][:5]:
                    context_parts.append(f"- {service}")
            
            if website_analysis.get('values'):
                context_parts.append("Wartości firmy:")
                for value in website_analysis['values'][:3]:
                    context_parts.append(f"- {value}")
            
            if website_analysis.get('target_audience'):
                context_parts.append(f"Grupa docelowa: {', '.join(website_analysis['target_audience'])}")
            
            if website_analysis.get('content_tone'):
                context_parts.append(f"Ton komunikacji na stronie: {website_analysis['content_tone']}")
            
            if website_analysis.get('key_topics'):
                context_parts.append("Kluczowe tematy ze strony:")
                for topic in website_analysis['key_topics'][:5]:
                    context_parts.append(f"- {topic}")
            
            context_parts.append("")  # Dodaj pustą linię dla separacji
    
    # Dodaj ogólny styl
    if communication_strategy.general_style:
        gs = communication_strategy.general_style
        context_parts.extend([
            f"Język komunikacji: {gs.language}",
            f"Ton: {gs.tone}",
            f"Treści techniczne: {gs.technical_content}",
            f"Employer branding: {gs.employer_branding_content}"
        ])
    
    # Dodaj persony
    if communication_strategy.personas:
        personas_desc = []
        for persona in communication_strategy.personas:
            personas_desc.append(f"- {persona.name}: {persona.description}")
        context_parts.append("Persony docelowe:\n" + "\n".join(personas_desc))
    
    # Dodaj cele komunikacyjne
    if hasattr(communication_strategy, 'communication_goals') and communication_strategy.communication_goals:
        goals_desc = [f"- {goal.goal_text}" for goal in communication_strategy.communication_goals]
        context_parts.append("Cele komunikacyjne:\n" + "\n".join(goals_desc))
    
    # Dodaj zasady CTA
    if communication_strategy.cta_rules:
        cta_desc = []
        for cta in communication_strategy.cta_rules:
            cta_desc.append(f"- {cta.content_type}: {cta.cta_text}")
        context_parts.append("Zasady Call-to-Action:\n" + "\n".join(cta_desc))
    
    # Dodaj informacje z briefu jeśli dostępne
    if content_plan_id and db:
        from app.db.crud_content_brief import content_brief_crud
        briefs = content_brief_crud.get_by_content_plan(db, content_plan_id)
        
        if briefs:
            context_parts.append("=== KRYTYCZNE INSTRUKCJE Z BRIEFU ===")
            for brief in briefs:
                if brief.ai_analysis:
                    analysis = brief.ai_analysis
                    
                    # Dodaj obowiązkowe tematy
                    mandatory = analysis.get("mandatory_topics", [])
                    if mandatory:
                        context_parts.append("OBOWIĄZKOWE TEMATY DO REALIZACJI:\n" + "\n".join([f"- {topic}" for topic in mandatory]))
                    
                    # Dodaj instrukcje
                    instructions = analysis.get("content_instructions", [])
                    if instructions:
                        context_parts.append("INSTRUKCJE TWORZENIA TREŚCI:\n" + "\n".join([f"- {inst}" for inst in instructions]))
                    
                    # Dodaj aktualności firmy
                    company_news = analysis.get("company_news", [])
                    if company_news:
                        context_parts.append("AKTUALNOŚCI FIRMY:\n" + "\n".join([f"- {news}" for news in company_news]))
                    
                    # Dodaj kluczowe komunikaty
                    key_messages = analysis.get("key_messages", [])
                    if key_messages:
                        context_parts.append("KLUCZOWE KOMUNIKATY:\n" + "\n".join([f"- {msg}" for msg in key_messages[:5]]))
    
    # SELEKTYWNE DODAWANIE INFORMACJI O PLATFORMACH
    # Dla blogów - nie dodawaj szczegółowych informacji o social media
    if is_blog_content:
        context_parts.append("\n=== WSKAZÓWKI DLA TREŚCI BLOGOWYCH ===")
        context_parts.append("- Artykuł powinien być obszerny (3000-6000 znaków)")
        context_parts.append("- Zachowaj strukturę z nagłówkami i akapitami")
        context_parts.append("- Pisz w stylu eksperckim, edukacyjnym")
        context_parts.append("- Unikaj bezpośredniej sprzedaży, skup się na wartości merytorycznej")
        context_parts.append("- Zakończ artykuł zachętą do kontaktu lub działania")
        
        # Nie dodawaj stylów platform social media
        logger.info("Filtering out social media platform styles for blog content")
    
    elif is_social_media and platform_name:
        # Dla social media - dodaj tylko informacje o konkretnej platformie
        context_parts.append(f"\n=== WSKAZÓWKI DLA {platform_name.upper()} ===")
        
        # Znajdź i dodaj tylko style dla tej platformy
        if communication_strategy.platform_styles:
            relevant_styles = [ps for ps in communication_strategy.platform_styles 
                             if ps.platform_name.lower() == platform_name.lower()]
            
            for ps in relevant_styles:
                context_parts.append(f"- Długość: {ps.length_description}")
                context_parts.append(f"- Styl: {ps.style_description}")
                if ps.notes:
                    context_parts.append(f"- Uwagi: {ps.notes}")
        
        # Nie dodawaj informacji o innych platformach social media
        logger.info(f"Added only {platform_name} specific guidelines, filtered out other platforms")
    
    else:
        # Domyślnie - dodaj wszystkie style platform (zachowanie legacy)
        if communication_strategy.platform_styles:
            platform_desc = []
            for ps in communication_strategy.platform_styles:
                platform_desc.append(f"- {ps.platform_name}: {ps.style_description} (długość: {ps.length_description})")
            if platform_desc:
                context_parts.append("Style platform:\n" + "\n".join(platform_desc))
    
    context = "\n\n".join(context_parts)
    
    # Zapisz w cache z uwzględnieniem typu
    cache_key_full = cache_key + ([platform_name] if platform_name else [])
    set_cached_context(cache_key_full, {"context": context})
    logger.info(f"Cached strategy context for strategy {communication_strategy.id}, type: {content_type}, platform: {platform_name}")
    
    return context


def get_platform_rules(platform_style: PlatformStyle) -> str:
    """
    Buduje zasady dla konkretnej platformy
    
    Args:
        platform_style: Style platformy z bazy danych
        
    Returns:
        str: Sformatowane zasady platformy
    """
    rules_parts = [
        f"Platforma: {platform_style.platform_name}",
        f"Długość treści: {platform_style.length_description}",
        f"Styl: {platform_style.style_description}"
    ]
    
    if platform_style.notes:
        rules_parts.append(f"Dodatkowe uwagi: {platform_style.notes}")
    
    return "\n".join(rules_parts)


def _call_gemini_api(prompt: str, model_name: str, max_retries: int = 3) -> Optional[str]:
    """
    Wywołuje API Gemini do generowania treści z retry logic
    
    Args:
        prompt: Prompt do wysłania
        model_name: Nazwa modelu (np. gemini-1.5-pro-latest)
        max_retries: Maximum number of retries for rate limiting
        
    Returns:
        Optional[str]: Odpowiedź z API lub None w przypadku błędu
    """
    if not GEMINI_API_AVAILABLE:
        logger.error("Gemini API not available. Please install google-generativeai.")
        return None
    
    # Konfiguracja API key z zmiennych środowiskowych
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        logger.error("GOOGLE_AI_API_KEY not found in environment variables")
        return None
    
    genai.configure(api_key=api_key)
    
    import time
    
    for attempt in range(max_retries):
        try:
            # Wybór modelu
            model = genai.GenerativeModel(model_name)
            
            # Wygenerowanie odpowiedzi
            response = model.generate_content(prompt)
            
            if response and response.text:
                return response.text.strip()
            else:
                logger.error("Empty response from Gemini API")
                return None
                
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for rate limiting error
            if any(keyword in error_str for keyword in ["quota", "429", "resource_exhausted", "rate_limit", "too many requests"]):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # Exponential backoff: 10s, 20s, 40s
                    logger.warning(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    logger.error(f"Rate limit exceeded after {max_retries} attempts")
                    return None
            else:
                logger.error(f"Error calling Gemini API: {str(e)}")
                return None
    
    return None


def generate_content_with_ai(
    prompt_template: str, 
    model_name: str,
    topic_title: str,
    topic_description: str, 
    general_strategy_context: str,
    platform_name: str,
    platform_rules: str,
    db: Session = None,
    content_type: str = "blog"
) -> Optional[str]:
    """
    Generuje treść używając AI
    
    Args:
        prompt_template: Szablon promptu
        model_name: Nazwa modelu AI
        topic_title: Tytuł tematu
        topic_description: Opis tematu
        general_strategy_context: Kontekst ogólnej strategii
        platform_name: Nazwa platformy
        platform_rules: Zasady platformy
        
    Returns:
        Optional[str]: Wygenerowana treść lub None w przypadku błędu
    """
    try:
        # Step 1: Use existing research from super_context instead of making new Tavily calls
        research_context = ""
        
        # OPTIMIZATION: Disable Tavily research for variants - research was already done during topic generation
        # This reduces Tavily API usage by ~97% (from 700+ to ~20 calls per content plan)
        logger.info(f"Using existing research from super_context for topic: {topic_title}")
        
        # Extract research data from super_context if available
        if super_context:
            # Check for research data in super_context
            research_data = super_context.get("research_data", {})
            website_analysis = super_context.get("organization", {}).get("website_analysis", {})
            
            if research_data or website_analysis:
                research_context = "\n\n=== INFORMACJE Z WCZEŚNIEJSZEGO RESEARCHU ===\n"
                
                # Add industry trends if available
                if research_data.get("industry_trends"):
                    research_context += f"Trendy branżowe: {research_data.get('industry_trends', '')[:300]}...\n"
                
                # Add market insights if available
                if research_data.get("market_insights"):
                    research_context += f"Insighty rynkowe: {research_data.get('market_insights', '')[:300]}...\n"
                
                # Add website analysis insights
                if website_analysis:
                    if website_analysis.get("key_topics"):
                        research_context += f"Kluczowe tematy firmy: {', '.join(website_analysis.get('key_topics', [])[:5])}\n"
                    if website_analysis.get("unique_selling_points"):
                        research_context += f"USP: {', '.join(website_analysis.get('unique_selling_points', [])[:3])}\n"
                    if website_analysis.get("recommended_content_topics"):
                        research_context += f"Rekomendowane tematy: {', '.join(website_analysis.get('recommended_content_topics', [])[:3])}\n"
                
                logger.info(f"Added existing research context: {len(research_context)} characters")
            else:
                logger.info("No existing research found in super_context, proceeding without additional research")
        
        # Step 2: Format prompt with all context including research
        formatted_prompt = prompt_template.replace("{topic_title}", topic_title)
        formatted_prompt = formatted_prompt.replace("{topic_description}", topic_description)
        formatted_prompt = formatted_prompt.replace("{general_strategy_context}", general_strategy_context + research_context)
        formatted_prompt = formatted_prompt.replace("{platform_name}", platform_name)
        formatted_prompt = formatted_prompt.replace("{platform_rules}", platform_rules)
        
        # Add temporal context at the end as a separate instruction
        temporal_context = get_temporal_context()
        formatted_prompt += f"\n\n{temporal_context}"
        
        # Step 3: Implement real Author-Reviewer loop
        logger.info(f"Starting Author-Reviewer loop for {platform_name}")
        
        # Author phase - initial content generation
        author_prompt = f"{formatted_prompt}\n\nROLA: Jesteś autorem treści. Stwórz angażującą treść zgodną z wytycznymi."
        
        initial_content = _call_gemini_api(author_prompt, model_name)
        if not initial_content:
            logger.error("Failed to generate initial content")
            return None
        
        # Parse initial response
        current_content = initial_content
        try:
            parsed_response = json.loads(initial_content)
            if isinstance(parsed_response, dict) and "content_text" in parsed_response:
                current_content = parsed_response["content_text"]
        except json.JSONDecodeError:
            pass  # Use raw response
        
        current_content = current_content.strip()
        logger.info(f"Author generated initial content: {len(current_content)} chars")
        
        # Check if AI generated multiple posts (common indicators) - ONLY for social media, NOT for blogs
        if platform_name.lower() != "blog" and content_type == "social_media":
            multiple_post_indicators = [
                "post 1:", "post 2:", "post 3:", "post 4:",
                "Post 1:", "Post 2:", "Post 3:", "Post 4:",
                "POST 1:", "POST 2:", "POST 3:", "POST 4:",
                "1.", "2.", "3.", "4.",
                "Wersja 1:", "Wersja 2:", "Wersja 3:",
                "Wariant 1:", "Wariant 2:", "Wariant 3:",
                "---", "***", "===",  # Common separators
            ]
            
            # Count how many indicators we find
            indicator_count = sum(1 for indicator in multiple_post_indicators if indicator in current_content)
            
            if indicator_count >= 2:
                logger.warning(f"Multiple posts detected in single variant for {platform_name}! Found {indicator_count} indicators")
                logger.warning(f"Content preview: {current_content[:200]}...")
                
                # Try to extract just the first post
                for separator in ["Post 2:", "post 2:", "POST 2:", "2.", "Wersja 2:", "Wariant 2:", "---", "***", "==="]:
                    if separator in current_content:
                        first_post = current_content.split(separator)[0].strip()
                        # Clean up any remaining numbering from the first post
                        for prefix in ["Post 1:", "post 1:", "POST 1:", "1.", "Wersja 1:", "Wariant 1:"]:
                            if first_post.startswith(prefix):
                                first_post = first_post[len(prefix):].strip()
                        
                        if first_post:
                            logger.info(f"Extracted first post only, reduced from {len(current_content)} to {len(first_post)} chars")
                            current_content = first_post
                            break
        
        # Skip reviewer loop for social media content
        if content_type == "social_media":
            logger.info(f"Skipping reviewer loop for social media content on {platform_name}")
            return current_content
        
        # Reviewer-Author improvement loop (only for blog content)
        max_improvements = 2
        for iteration in range(max_improvements):
            logger.info(f"Reviewer iteration {iteration + 1}/{max_improvements}")
            
            # Reviewer phase
            reviewer_prompt = f"""ROLA: Jesteś recenzentem treści marketingowych.

TREŚĆ DO OCENY:
{current_content}

KONTEKST:
{general_strategy_context}
{research_context}

PLATFORMA: {platform_name}
ZASADY PLATFORMY: {platform_rules}

Oceń tę treść pod kątem:
1. Zgodności ze strategią komunikacji i briefem
2. Atrakcyjności i zaangażowania odbiorców
3. Poprawności merytorycznej (wykorzystaj research z Tavily)
4. Optymalizacji pod platformę {platform_name}
5. Obecności kluczowych komunikatów z briefu

Jeśli treść jest doskonała, napisz "ZATWIERDZONA".
Jeśli wymaga poprawek, podaj KONKRETNE uwagi do poprawy."""
            
            review_feedback = _call_gemini_api(reviewer_prompt, model_name)
            if not review_feedback:
                logger.warning(f"No reviewer feedback at iteration {iteration + 1}")
                break
            
            # Check if approved
            if "ZATWIERDZONA" in review_feedback.upper():
                logger.info(f"Content approved by reviewer at iteration {iteration + 1}")
                break
            
            # Author improvement phase
            improvement_prompt = f"""ROLA: Jesteś autorem poprawiającym treść.

OBECNA TREŚĆ:
{current_content}

UWAGI RECENZENTA:
{review_feedback}

KONTEKST (przypomnenie):
{general_strategy_context}
{research_context}

Popraw treść zgodnie z uwagami recenzenta, zachowując wszystkie wymagania.
Zwróć TYLKO poprawioną treść, bez wyjaśnień."""
            
            improved_content = _call_gemini_api(improvement_prompt, model_name)
            if improved_content and improved_content.strip():
                current_content = improved_content.strip()
                logger.info(f"Content improved at iteration {iteration + 1}: {len(current_content)} chars")
            else:
                logger.warning(f"Failed to improve content at iteration {iteration + 1}")
                break
        
        logger.info(f"Author-Reviewer loop completed for {platform_name}")
        return current_content
        
    except Exception as e:
        logger.error(f"Error in generate_content_with_ai for platform {platform_name}: {str(e)}")
        return None


@celery_app.task(name="generate_all_variants_for_topic_task")
def generate_all_variants_for_topic_task(topic_id: int) -> Dict[str, Any]:
    """
    Główne zadanie Celery do generowania wszystkich wariantów treści dla tematu
    
    Args:
        topic_id: ID tematu (SuggestedTopic)
        
    Returns:
        Dict z rezultatem operacji
    """
    db = next(get_db())
    
    try:
        # Pobierz temat wraz z powiązaną strategią komunikacji
        suggested_topic = db.query(SuggestedTopic).options(
            joinedload(SuggestedTopic.content_plan)
        ).filter(
            SuggestedTopic.id == topic_id
        ).first()
        
        if not suggested_topic:
            logger.error(f"SuggestedTopic with id {topic_id} not found")
            return {"success": False, "error": "Topic not found"}
        
        if suggested_topic.status != "approved":
            logger.error(f"SuggestedTopic {topic_id} is not approved (status: {suggested_topic.status})")
            logger.error(f"Refusing to generate content for unapproved topic: {suggested_topic.title}")
            return {"success": False, "error": "Topic not approved"}
        
        logger.info(f"✓ Topic {topic_id} is approved. Title: {suggested_topic.title}")
        logger.info(f"Starting content generation for approved topic in category: {suggested_topic.category}")
        
        # Pobierz organization_id z content_plan
        organization_id = suggested_topic.content_plan.organization_id
        
        # Pobierz strategię komunikacji dla organizacji
        communication_strategy = db.query(CommunicationStrategy).options(
            joinedload(CommunicationStrategy.general_style),
            joinedload(CommunicationStrategy.personas),
            joinedload(CommunicationStrategy.platform_styles),
            joinedload(CommunicationStrategy.cta_rules)
        ).filter(
            CommunicationStrategy.organization_id == organization_id,
            CommunicationStrategy.is_active == True
        ).first()
        
        if not communication_strategy:
            logger.error(f"No active communication strategy found for organization {organization_id}")
            return {"success": False, "error": "No communication strategy found"}
        
        if not communication_strategy.platform_styles:
            logger.error(f"No platform styles found in communication strategy {communication_strategy.id}")
            return {"success": False, "error": "No platform styles configured"}
        
        # Pobierz prompt i model AI
        ai_prompt = db.query(AIPrompt).filter(
            AIPrompt.prompt_name == "generate_single_variant"
        ).first()
        
        if not ai_prompt:
            logger.error("AI prompt 'generate_single_variant' not found")
            return {"success": False, "error": "AI prompt not configured"}
        
        ai_model_assignment = db.query(AIModelAssignment).filter(
            AIModelAssignment.task_name == "generate_single_variant"
        ).first()
        
        if not ai_model_assignment:
            logger.error("AI model assignment for 'generate_single_variant' not found")
            return {"success": False, "error": "AI model not configured"}
        
        # Stwórz nadrzędny ContentDraft
        content_draft = ContentDraft(
            suggested_topic_id=topic_id,
            status="drafting",
            created_by_task_id=current_app.current_task.request.id if hasattr(current_app, 'current_task') else None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(content_draft)
        db.flush()  # Flush aby uzyskać ID
        
        logger.info(f"Created ContentDraft {content_draft.id} for topic {topic_id}")
        
        # Przygotuj kontekst ogólnej strategii
        # Determine content type based on category
        content_type = "blog" if suggested_topic.category == "blog" else "social_media"
        
        general_strategy_context = get_general_strategy_context(
            communication_strategy, 
            content_plan_id=suggested_topic.content_plan_id,
            db=db,
            content_type=content_type
        )
        
        # Pętla po wszystkich platformach z filtrowaniem
        variants_created = 0
        variants_failed = 0
        
        # Group platform styles by platform name to limit variants per platform
        platform_groups = {}
        for ps in communication_strategy.platform_styles:
            if should_generate_for_platform(ps.platform_name, suggested_topic.category):
                platform_name_lower = ps.platform_name.lower()
                if platform_name_lower not in platform_groups:
                    platform_groups[platform_name_lower] = []
                platform_groups[platform_name_lower].append(ps)
        
        # Limit to max 2 variants per platform type (configurable)
        # This prevents generating too many variants when multiple platform styles exist for the same platform
        # For social media correlated with blog posts, limit to 1 variant per platform
        if suggested_topic.category == "social_media" and suggested_topic.parent_topic_id:
            MAX_VARIANTS_PER_PLATFORM = 1
        else:
            MAX_VARIANTS_PER_PLATFORM = int(os.getenv('MAX_VARIANTS_PER_PLATFORM', '2'))
        
        # Process platform styles with limits
        for platform_name_lower, platform_styles_list in platform_groups.items():
            # Take only the first MAX_VARIANTS_PER_PLATFORM styles for each platform
            limited_styles = platform_styles_list[:MAX_VARIANTS_PER_PLATFORM]
            
            if len(platform_styles_list) > MAX_VARIANTS_PER_PLATFORM:
                logger.info(f"Limiting {platform_name_lower} variants from {len(platform_styles_list)} to {MAX_VARIANTS_PER_PLATFORM}")
            
            for platform_style in limited_styles:
                try:
                    logger.info(f"Generating variant for platform: {platform_style.platform_name}")
                    
                    # Przygotuj zasady dla platformy
                    platform_rules = get_platform_rules(platform_style)
                    
                    # Generuj treść używając AI
                    generated_content = generate_content_with_ai(
                        prompt_template=ai_prompt.prompt_template,
                        model_name=ai_model_assignment.model_name,
                        topic_title=suggested_topic.title,
                        topic_description=suggested_topic.description or "",
                        general_strategy_context=general_strategy_context,
                        platform_name=platform_style.platform_name,
                        platform_rules=platform_rules,
                        db=db,
                        content_type=content_type
                    )
                    
                    if not generated_content:
                        logger.error(f"Failed to generate content for platform {platform_style.platform_name}")
                        variants_failed += 1
                        continue
                    
                    # Stwórz ContentVariant
                    content_variant = ContentVariant(
                        content_draft_id=content_draft.id,
                        platform_name=platform_style.platform_name,
                        content_text=generated_content,
                        status="pending_approval",
                        version=1,
                        created_by_task_id=current_app.current_task.request.id if hasattr(current_app, 'current_task') else None,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(content_variant)
                    variants_created += 1
                    
                    logger.info(f"Created ContentVariant for platform {platform_style.platform_name}")
                    
                except Exception as e:
                    logger.error(f"Error generating variant for platform {platform_style.platform_name}: {str(e)}")
                    variants_failed += 1
                    continue
        
        # Zaktualizuj status ContentDraft
        if variants_created > 0:
            content_draft.status = "pending_approval"
            content_draft.updated_at = datetime.utcnow()
            logger.info(f"Updated ContentDraft {content_draft.id} status to pending_approval")
        else:
            content_draft.status = "failed"
            content_draft.updated_at = datetime.utcnow()
            logger.error(f"No variants created for ContentDraft {content_draft.id}")
        
        db.commit()
        
        result = {
            "success": variants_created > 0,
            "content_draft_id": content_draft.id,
            "variants_created": variants_created,
            "variants_failed": variants_failed,
            "total_platforms": len(communication_strategy.platform_styles)
        }
        
        logger.info(f"Completed generating variants for topic {topic_id}: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_all_variants_for_topic_task for topic {topic_id}: {str(e)}")
        db.rollback()
        return {"success": False, "error": str(e)}
    
    finally:
        db.close() 


@celery_app.task(name="generate_single_variant_task")
def generate_single_variant_task(
    suggested_topic_id: int, 
    platform_name: str, 
    revision_mode: Optional[str] = None,
    revision_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Zadanie Celery do generowania pojedynczego wariantu treści dla określonej platformy
    
    Args:
        suggested_topic_id: ID tematu (SuggestedTopic) 
        platform_name: Nazwa platformy do generowania
        revision_mode: Tryb rewizji ('feedback', 'regenerate', None)
        revision_context: Kontekst rewizji (feedback, previous_content, etc.)
        
    Returns:
        Dict z rezultatem operacji
    """
    db = next(get_db())
    
    try:
        # Pobierz temat wraz z powiązaną strategią komunikacji
        suggested_topic = db.query(SuggestedTopic).options(
            joinedload(SuggestedTopic.content_plan)
        ).filter(
            SuggestedTopic.id == suggested_topic_id
        ).first()
        
        if not suggested_topic:
            logger.error(f"SuggestedTopic with id {suggested_topic_id} not found")
            return {"success": False, "error": "Topic not found"}
        
        # Pobierz organization_id z content_plan
        organization_id = suggested_topic.content_plan.organization_id
        
        # Pobierz strategię komunikacji dla organizacji
        communication_strategy = db.query(CommunicationStrategy).options(
            joinedload(CommunicationStrategy.general_style),
            joinedload(CommunicationStrategy.personas),
            joinedload(CommunicationStrategy.platform_styles),
            joinedload(CommunicationStrategy.cta_rules)
        ).filter(
            CommunicationStrategy.organization_id == organization_id,
            CommunicationStrategy.is_active == True
        ).first()
        
        if not communication_strategy:
            logger.error(f"No active communication strategy found for organization {organization_id}")
            return {"success": False, "error": "No communication strategy found"}
        
        # Znajdź odpowiedni PlatformStyle
        platform_style = None
        for ps in communication_strategy.platform_styles:
            if ps.platform_name == platform_name:
                platform_style = ps
                break
        
        if not platform_style:
            logger.error(f"Platform style for '{platform_name}' not found in communication strategy")
            return {"success": False, "error": f"Platform '{platform_name}' not configured"}
        
        # Wybierz odpowiedni prompt na podstawie revision_mode
        if revision_mode == 'feedback':
            prompt_name = "revise_single_variant_with_feedback"
        elif revision_mode == 'regenerate':
            prompt_name = "regenerate_single_variant"
        else:
            prompt_name = "generate_single_variant"
        
        # Pobierz prompt i model AI
        ai_prompt = db.query(AIPrompt).filter(
            AIPrompt.prompt_name == prompt_name
        ).first()
        
        if not ai_prompt:
            logger.error(f"AI prompt '{prompt_name}' not found")
            return {"success": False, "error": f"AI prompt '{prompt_name}' not configured"}
        
        ai_model_assignment = db.query(AIModelAssignment).filter(
            AIModelAssignment.task_name == prompt_name
        ).first()
        
        if not ai_model_assignment:
            logger.error(f"AI model assignment for '{prompt_name}' not found")
            return {"success": False, "error": f"AI model for '{prompt_name}' not configured"}
        
        # Znajdź lub stwórz ContentDraft
        content_draft = None
        if revision_context and revision_context.get('variant_id'):
            # Jeśli to rewizja istniejącego wariantu, znajdź ContentDraft
            existing_variant = db.query(ContentVariant).filter(
                ContentVariant.id == revision_context['variant_id']
            ).first()
            
            if existing_variant:
                content_draft = db.query(ContentDraft).filter(
                    ContentDraft.id == existing_variant.content_draft_id
                ).first()
        
        if not content_draft:
            # Stwórz nowy ContentDraft
            content_draft = ContentDraft(
                suggested_topic_id=suggested_topic_id,
                status="drafting",
                created_by_task_id=current_app.current_task.request.id if hasattr(current_app, 'current_task') else None,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(content_draft)
            db.flush()  # Flush aby uzyskać ID
            
            logger.info(f"Created ContentDraft {content_draft.id} for topic {suggested_topic_id}")
        
        # Przygotuj kontekst ogólnej strategii
        # Determine content type based on category and platform
        content_type = "blog" if suggested_topic.category == "blog" else "social_media"
        
        general_strategy_context = get_general_strategy_context(
            communication_strategy, 
            content_plan_id=suggested_topic.content_plan_id,
            db=db,
            platform_name=platform_name,
            content_type=content_type
        )
        
        # Przygotuj zasady dla platformy
        platform_rules = get_platform_rules(platform_style)
        
        # Przygotuj prompt w zależności od revision_mode
        if revision_mode == 'feedback' and revision_context:
            # Rozszerz prompt o feedback
            prompt_template = ai_prompt.prompt_template + f"""
            
FEEDBACK DO UWZGLĘDNIENIA:
{revision_context.get('feedback', '')}

POPRZEDNIA WERSJA TREŚCI:
{revision_context.get('previous_content', '')}

Uwzględnij feedback i popraw treść zgodnie z uwagami.
"""
        elif revision_mode == 'regenerate' and revision_context:
            # Rozszerz prompt o informację o regeneracji
            prompt_template = ai_prompt.prompt_template + f"""
            
POPRZEDNIA WERSJA TREŚCI (do odniesienia):
{revision_context.get('previous_content', '')}

Wygeneruj nową, lepszą wersję treści dla tej samej platformy.
"""
        else:
            prompt_template = ai_prompt.prompt_template
        
        logger.info(f"Generating variant for platform: {platform_name}, mode: {revision_mode}")
        
        # Generuj treść używając AI
        generated_content = generate_content_with_ai(
            prompt_template=prompt_template,
            model_name=ai_model_assignment.model_name,
            topic_title=suggested_topic.title,
            topic_description=suggested_topic.description or "",
            general_strategy_context=general_strategy_context,
            platform_name=platform_name,
            platform_rules=platform_rules,
            db=db,
            content_type=content_type
        )
        
        if not generated_content:
            logger.error(f"Failed to generate content for platform {platform_name}")
            return {"success": False, "error": f"Failed to generate content for platform {platform_name}"}
        
        # Stwórz ContentVariant
        content_variant = ContentVariant(
            content_draft_id=content_draft.id,
            platform_name=platform_name,
            content_text=generated_content,
            status="pending_approval",
            version=1,
            created_by_task_id=current_app.current_task.request.id if hasattr(current_app, 'current_task') else None,
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(content_variant)
        
        # Zaktualizuj status ContentDraft
        content_draft.status = "pending_approval"
        content_draft.updated_at = datetime.utcnow()
        
        db.commit()
        
        result = {
            "success": True,
            "content_draft_id": content_draft.id,
            "variant_id": content_variant.id,
            "platform_name": platform_name,
            "revision_mode": revision_mode,
            "content_length": len(generated_content),
            "message": f"Successfully generated variant for platform {platform_name}"
        }
        
        logger.info(f"Completed generating single variant: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error in generate_single_variant_task: {str(e)}")
        db.rollback()
        return {"success": False, "error": str(e)}
    
    finally:
        db.close() 