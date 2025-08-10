"""
Main flow tasks for content generation system.
Implements the chained tasks for blog topics generation with AI.
"""

import json
import logging
from typing import Dict, Any, List
from datetime import datetime

from celery import shared_task
from sqlalchemy.orm import Session, joinedload

from app.db.database import SessionLocal
from app.db import crud, models
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService
from app.tasks.content_generation import _call_gemini_api  # Reuse existing Gemini integration
from app.tasks.variant_generation import generate_all_variants_for_topic_task
from app.core.external_integrations import ContentResearchOrchestrator

# Configure logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, name="content_gen.contextualize_task")
def contextualize_task(self, plan_id: int) -> Dict[str, Any]:
    """
    Task 1: Contextualize - gather all context data for content generation.
    
    Retrieves ContentPlan, associated CommunicationStrategy, and prepares
    the "Super-Context" for AI content generation.
    
    Args:
        plan_id: ID of the ContentPlan to process
        
    Returns:
        Dict containing super_context and metadata
    """
    logger.info(f"Starting contextualize_task for plan_id: {plan_id}")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Get ContentPlan
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if not content_plan:
                raise ValueError(f"ContentPlan with ID {plan_id} not found")
            
            logger.info(f"Found ContentPlan: {content_plan.plan_period}")
            
            # Get Organization
            organization = crud.organization_crud.get_by_id(db, content_plan.organization_id)
            if not organization:
                raise ValueError(f"Organization with ID {content_plan.organization_id} not found")
            
            # Get website analysis if available
            from app.tasks.website_analysis import get_website_analysis_for_organization
            website_analysis = get_website_analysis_for_organization(db, organization.id)
            
            if website_analysis:
                logger.info(f"Found website analysis for organization {organization.id}")
                logger.info(f"  - Industry detected: {website_analysis.get('industry')}")
                logger.info(f"  - Services count: {len(website_analysis.get('services', []))}")
                logger.info(f"  - Key topics count: {len(website_analysis.get('key_topics', []))}")
            else:
                logger.info(f"No website analysis found for organization {organization.id}")
            
            # Get associated CommunicationStrategy
            # Find the most recent active strategy for this organization
            strategies = db.query(models.CommunicationStrategy).filter(
                models.CommunicationStrategy.organization_id == content_plan.organization_id,
                models.CommunicationStrategy.is_active == True
            ).order_by(models.CommunicationStrategy.created_at.desc()).limit(1).all()
            
            strategy = strategies[0] if strategies else None
            
            if not strategy:
                logger.warning(f"No active CommunicationStrategy found for organization {content_plan.organization_id}")
                strategy_context = {
                    "strategy_name": "Default Strategy",
                    "description": "No specific communication strategy defined",
                    "communication_goals": ["Increase brand awareness", "Generate leads"],
                    "target_audiences": [{"name": "General Audience", "description": "Broad target audience"}],
                    "general_style": {
                        "language": "polski",
                        "tone": "profesjonalny",
                        "technical_content": "dostępny dla wszystkich",
                        "employer_branding_content": "wykazujący ekspertyze"
                    },
                    "platform_styles": [],
                    "forbidden_phrases": [],
                    "preferred_phrases": [],
                    "cta_rules": []
                }
            else:
                # Get all related data for the strategy
                personas = db.query(models.Persona).filter(
                    models.Persona.communication_strategy_id == strategy.id
                ).all()
                
                platform_styles = db.query(models.PlatformStyle).filter(
                    models.PlatformStyle.communication_strategy_id == strategy.id
                ).all()
                
                cta_rules = db.query(models.CTARule).filter(
                    models.CTARule.communication_strategy_id == strategy.id
                ).all()
                
                general_style = db.query(models.GeneralStyle).filter(
                    models.GeneralStyle.communication_strategy_id == strategy.id
                ).first()
                
                # Get communication goals
                communication_goals = db.query(models.CommunicationGoal).filter(
                    models.CommunicationGoal.communication_strategy_id == strategy.id
                ).all()
                
                # Get forbidden phrases
                forbidden_phrases = db.query(models.ForbiddenPhrase).filter(
                    models.ForbiddenPhrase.communication_strategy_id == strategy.id
                ).all()
                
                # Get preferred phrases
                preferred_phrases = db.query(models.PreferredPhrase).filter(
                    models.PreferredPhrase.communication_strategy_id == strategy.id
                ).all()
                
                strategy_context = {
                    "strategy_name": strategy.name,
                    "description": strategy.description or "",
                    "communication_goals": [goal.goal_text for goal in communication_goals],
                    "target_audiences": [
                        {"name": persona.name, "description": persona.description} 
                        for persona in personas
                    ],
                    "general_style": {
                        "language": general_style.language if general_style else "polski",
                        "tone": general_style.tone if general_style else "profesjonalny",
                        "technical_content": general_style.technical_content if general_style else "dostępny",
                        "employer_branding_content": general_style.employer_branding_content if general_style else "ekspercki"
                    },
                    "platform_styles": [
                        {
                            "platform_name": ps.platform_name,
                            "length_description": ps.length_description,
                            "style_description": ps.style_description,
                            "notes": ps.notes or ""
                        }
                        for ps in platform_styles
                    ],
                    "forbidden_phrases": [fp.phrase for fp in forbidden_phrases],
                    "preferred_phrases": [pp.phrase for pp in preferred_phrases],
                    "cta_rules": [
                        {"content_type": cta.content_type, "cta_text": cta.cta_text}
                        for cta in cta_rules
                    ]
                }
            
            # Get rejected topics to avoid similar suggestions
            rejected_topics = db.query(models.SuggestedTopic).filter(
                models.SuggestedTopic.content_plan_id == plan_id,
                models.SuggestedTopic.status == 'rejected',
                models.SuggestedTopic.is_active == True
            ).all()
            
            rejected_topics_context = [
                {
                    "title": topic.title,
                    "description": topic.description,
                    "rejected_reason": "User marked as rejected - avoid similar topics"
                }
                for topic in rejected_topics
            ]
            
            # Get briefs for enhanced context
            from app.db.crud_content_brief import content_brief_crud
            briefs = content_brief_crud.get_by_content_plan(db, plan_id)
            
            logger.info(f"Found {len(briefs)} briefs for content plan {plan_id}")
            
            # Wait for brief analysis to complete if briefs exist
            if briefs:
                import time
                max_wait_time = 30  # Maximum 30 seconds wait
                wait_interval = 2   # Check every 2 seconds
                waited_time = 0
                
                for brief in briefs:
                    while not brief.ai_analysis and waited_time < max_wait_time:
                        logger.info(f"Waiting for brief {brief.id} analysis to complete... ({waited_time}s)")
                        time.sleep(wait_interval)
                        waited_time += wait_interval
                        
                        # Refresh brief data from database
                        db.refresh(brief)
                        
                    if not brief.ai_analysis and waited_time >= max_wait_time:
                        logger.warning(f"Brief {brief.id} analysis timeout after {max_wait_time}s - continuing anyway")
            
            brief_context = {
                "has_briefs": len(briefs) > 0,
                "brief_count": len(briefs),
                "mandatory_topics": [],  # Add mandatory topics
                "content_instructions": [],  # Add content instructions
                "company_news": [],  # Add company news
                "key_messages": [],  # Add key messages
                "key_topics": [],
                "priority_items": [],
                "important_context": [],
                "raw_content": []  # Add raw content for better visibility
            }
            
            # Aggregate brief insights
            for brief in briefs:
                logger.info(f"Processing brief: {brief.title} with priority: {brief.priority_level}")
                
                # Add raw content if available
                if brief.file_path:
                    try:
                        # Use extracted_content if available (already parsed text)
                        if brief.extracted_content:
                            content_preview = brief.extracted_content[:1000]  # First 1000 chars
                            brief_context["raw_content"].append({
                                "title": brief.title,
                                "content_preview": content_preview
                            })
                        else:
                            # Skip binary files for now - they should be processed by analyze_brief_task
                            logger.info(f"Brief {brief.id} has no extracted content yet")
                    except Exception as e:
                        logger.error(f"Error reading brief content: {e}")
                
                if brief.ai_analysis:
                    analysis = brief.ai_analysis
                    logger.info(f"Brief analysis found: {json.dumps(analysis, ensure_ascii=False)[:500]}")
                    
                    # Extract all the new fields
                    brief_context["mandatory_topics"].extend(analysis.get("mandatory_topics", []))
                    brief_context["content_instructions"].extend(analysis.get("content_instructions", []))
                    brief_context["company_news"].extend(analysis.get("company_news", []))
                    brief_context["key_messages"].extend(analysis.get("key_messages", []))
                    brief_context["key_topics"].extend(analysis.get("key_topics", [])[:5])
                    brief_context["priority_items"].extend(analysis.get("priority_items", [])[:3])
                    
                    brief_context["important_context"].append({
                        "title": brief.title,
                        "priority": brief.priority_level,
                        "summary": analysis.get("context_summary", ""),
                        "mandatory_topics_count": len(analysis.get("mandatory_topics", []))
                    })
                else:
                    logger.warning(f"No AI analysis for brief {brief.id}")
            
            # Remove duplicates while preserving order for important fields
            brief_context["mandatory_topics"] = list(dict.fromkeys(brief_context["mandatory_topics"]))
            brief_context["content_instructions"] = list(dict.fromkeys(brief_context["content_instructions"]))
            brief_context["company_news"] = list(dict.fromkeys(brief_context["company_news"]))
            brief_context["key_messages"] = list(dict.fromkeys(brief_context["key_messages"]))
            brief_context["key_topics"] = list(dict.fromkeys(brief_context["key_topics"]))
            brief_context["priority_items"] = list(dict.fromkeys(brief_context["priority_items"]))
            
            # Build Super-Context
            super_context = {
                "organization": {
                    "name": organization.name,
                    "description": organization.description or "",
                    "industry": website_analysis.get('industry') if website_analysis else organization.industry or "",
                    "website": organization.website or "",
                    "website_analysis": website_analysis if website_analysis else None
                },
                "content_plan": {
                    "plan_period": content_plan.plan_period,
                    "blog_posts_quota": content_plan.blog_posts_quota,
                    "sm_posts_quota": content_plan.sm_posts_quota,
                    "correlate_posts": content_plan.correlate_posts,
                    "scheduling_mode": content_plan.scheduling_mode,
                    "status": content_plan.status
                },
                "communication_strategy": strategy_context,
                "rejected_topics": rejected_topics_context,
                "brief_insights": brief_context,
                "research_data": {
                    # Placeholder for RAGFlow integration
                    "industry_trends": "Dane z RAGFlow będą tutaj dostępne w przyszłości",
                    "competitor_analysis": "Analiza konkurencji z RAGFlow",
                    "market_insights": "Insights rynkowe z zewnętrznych źródeł"
                }
            }
            
            logger.info("Successfully built super-context")
            logger.info(f"Brief context summary:")
            logger.info(f"  - Has briefs: {brief_context['has_briefs']}")
            logger.info(f"  - Brief count: {brief_context['brief_count']}")
            logger.info(f"  - Mandatory topics: {len(brief_context['mandatory_topics'])}")
            logger.info(f"  - Content instructions: {len(brief_context['content_instructions'])}")
            logger.info(f"  - Company news: {len(brief_context['company_news'])}")
            logger.info(f"  - Key messages: {len(brief_context['key_messages'])}")
            logger.info(f"Communication strategy summary:")
            logger.info(f"  - Goals: {len(strategy_context.get('communication_goals', []))}")
            logger.info(f"  - Target audiences: {len(strategy_context.get('target_audiences', []))}")
            logger.info(f"  - Platform styles: {len(strategy_context.get('platform_styles', []))}")
            
            # Log example content from brief for verification
            if brief_context['mandatory_topics']:
                logger.info(f"Example mandatory topics: {brief_context['mandatory_topics'][:2]}")
            if brief_context['content_instructions']:
                logger.info(f"Example content instructions: {brief_context['content_instructions'][:2]}")
            if brief_context['company_news']:
                logger.info(f"Example company news: {brief_context['company_news'][:2]}")
            
            return {
                "super_context": super_context,
                "plan_id": plan_id,
                "organization_id": content_plan.organization_id,
                "blog_posts_quota": content_plan.blog_posts_quota,
                "topics_to_generate": content_plan.blog_posts_quota
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in contextualize_task: {str(e)}")
        self.retry(countdown=60, max_retries=3)


@shared_task(bind=True, name="content_gen.generate_and_save_blog_topics_task")
def generate_and_save_blog_topics_task(self, context_data: Dict[str, Any], plan_id: int) -> Dict[str, Any]:
    """
    Task 2: Generate and save blog topics using AI.
    
    Uses ResearchAgent + Tavily for additional research, then calls Gemini API
    to generate blog topics based on the super-context.
    
    Args:
        context_data: Super-context from previous task
        plan_id: ID of the ContentPlan to update
        
    Returns:
        Dict with task results and generated topics count
    """
    logger.info(f"Starting generate_and_save_blog_topics_task for plan_id: {plan_id}")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Get plan details
            plan_id = context_data.get("plan_id", plan_id)
            organization_id = context_data["organization_id"]
            quota = context_data.get('blog_posts_quota', 1) 
            topics_to_generate = quota + 3 
            super_context = context_data["super_context"]
            
            # Check if deep reasoning is enabled
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            use_deep_reasoning = False
            if content_plan and content_plan.meta_data:
                generation_method = content_plan.meta_data.get('generation_method', 'standard')
                use_deep_reasoning = (generation_method == 'deep_reasoning')
                logger.info(f"Generation method: {generation_method}, use_deep_reasoning: {use_deep_reasoning}")
            
            # Enhanced research with Tavily or Deep Reasoning
            if use_deep_reasoning:
                logger.info("Using Deep Reasoning Engine for topic generation")
                from app.core.deep_reasoning import DeepReasoningEngine
                import asyncio
                
                reasoning_engine = DeepReasoningEngine(db)
                
                # Run async method in sync context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    reasoning_result = loop.run_until_complete(
                        reasoning_engine.analyze_with_reasoning(
                            context=super_context,
                            task_type="generate_topics"
                        )
                    )
                finally:
                    loop.close()
                
                # Extract topics from reasoning result
                enhanced_context = reasoning_result.get('final_output', super_context)
                logger.info(f"Deep reasoning completed with {len(reasoning_result.get('reasoning_steps', []))} steps")
            else:
                # Standard generation with basic research
                enhanced_context = _enhance_context_with_research(super_context)
            
            # Get AI prompt and model
            prompt_manager = PromptManager(db)
            ai_config = AIConfigService(db)
            
            prompt_template = prompt_manager._get_cached_prompt("generate_blog_topics_for_selection")
            model_name = ai_config._get_cached_model("generate_blog_topics_for_selection")
            
            if not prompt_template:
                raise ValueError("AI prompt 'generate_blog_topics_for_selection' not found")
            
            if not model_name:
                raise ValueError("AI model assignment 'generate_blog_topics_for_selection' not found")
            
            logger.info(f"Using model: {model_name}")
            
            # Log brief content for debugging
            brief_data = enhanced_context.get('brief_insights', {})
            logger.info(f"Brief insights found: has_briefs={brief_data.get('has_briefs')}, brief_count={brief_data.get('brief_count')}")
            logger.info(f"Brief mandatory topics: {brief_data.get('mandatory_topics', [])}")
            logger.info(f"Brief content instructions: {brief_data.get('content_instructions', [])}")
            logger.info(f"Brief company news: {brief_data.get('company_news', [])}")
            logger.info(f"Brief key messages: {brief_data.get('key_messages', [])}")
            logger.info(f"Brief key topics: {brief_data.get('key_topics', [])}")
            logger.info(f"Brief priority items: {brief_data.get('priority_items', [])}")
            
            # Extract and format individual context elements
            org = enhanced_context.get("organization", {})
            brief = enhanced_context.get("brief_insights", {})
            strategy = enhanced_context.get("communication_strategy", {})
            rejected = enhanced_context.get("rejected_topics", [])
            
            # Format lists and complex data
            def format_list(items):
                if not items:
                    return "Brak danych"
                return "\n".join(f"- {item}" for item in items[:10])  # Limit to 10 items
            
            def format_personas(personas):
                if not personas:
                    return "Brak zdefiniowanych person"
                return "\n".join(f"- {p.get('name', '')}: {p.get('description', '')[:100]}..." for p in personas[:5])
            
            # Get brief content from database
            brief_content = "Brak treści briefu"
            if brief.get("has_briefs") and content_plan:
                # Get briefs from database
                briefs = db.query(models.ContentBrief).filter(
                    models.ContentBrief.content_plan_id == plan_id
                ).all()
                
                if briefs:
                    # Combine all brief contents
                    brief_texts = []
                    for b in briefs:
                        if b.extracted_content:
                            brief_texts.append(f"=== {b.title} ===\n{b.extracted_content[:2000]}...")  # Limit each brief
                    
                    if brief_texts:
                        brief_content = "\n\n".join(brief_texts)
            
            # Build formatted super context for the prompt
            formatted_super_context = {
                "organization": {
                    "name": org.get("name", "Nieznana"),
                    "industry": org.get("industry", "Nieznana"),
                    "description": org.get("description", "Brak opisu"),
                    "website_insights": org.get("website_analysis") if org.get("website_analysis") else None
                },
                "brief_insights": {
                    "has_briefs": brief.get("has_briefs", False),
                    "brief_content": brief_content,
                    "mandatory_topics": brief.get("mandatory_topics", []),
                    "content_instructions": brief.get("content_instructions", []),
                    "company_news": brief.get("company_news", []),
                    "key_messages": brief.get("key_messages", []),
                    "key_topics": brief.get("key_topics", []),
                    "priority_items": brief.get("priority_items", [])
                },
                "communication_strategy": {
                    "communication_goals": strategy.get("communication_goals", []),
                    "target_audiences": strategy.get("target_audiences", []),
                    "preferred_phrases": strategy.get("preferred_phrases", []),
                    "forbidden_phrases": strategy.get("forbidden_phrases", [])
                },
                "rejected_topics": rejected,
                "research_data": enhanced_context.get("research_data", {}),
                "ai_research_suggestions": enhanced_context.get("ai_research_suggestions", {})
            }
            
            # Log the final super context being sent to AI
            logger.info(f"Super context being sent to AI: {json.dumps(formatted_super_context, ensure_ascii=False)[:1000]}...")
            
            # Add temporal context to the prompt
            from app.tasks.variant_generation import get_temporal_context
            temporal_context = get_temporal_context()
            
            # Replace template variables according to the new prompt format
            final_prompt = prompt_template
            final_prompt = final_prompt.replace("{super_context}", json.dumps(formatted_super_context, ensure_ascii=False, indent=2))
            final_prompt = final_prompt.replace("{topics_to_generate}", str(topics_to_generate))
            
            # Add temporal context at the end of the prompt with clear instructions
            final_prompt += f"\n\n{temporal_context}"
            final_prompt += "\n\nPAMIĘTAJ: Kontekst czasowy służy TYLKO do uniknięcia nieodpowiednich tematów. NIE wspominaj o porze roku w każdym temacie."
            
            # Note: Research insights are already included in the formatted_super_context above
            
            logger.info(f"Plan ID {plan_id}: Requesting {topics_to_generate} blog topics (Quota: {quota}).")
            logger.info(f"Prompt length: {len(final_prompt)} characters")
            logger.info("Calling Gemini API for blog topics generation")
            
            # Log to verify brief is in the prompt
            if "mandatory_topics" in final_prompt:
                logger.info("✓ Mandatory topics found in prompt")
            if "content_instructions" in final_prompt:
                logger.info("✓ Content instructions found in prompt")
            if "company_news" in final_prompt:
                logger.info("✓ Company news found in prompt")
            
            # Call Gemini API
            gemini_response = _call_gemini_api(final_prompt, model_name)
            
            if not gemini_response:
                raise ValueError("Gemini API returned empty response")
            
            # Parse JSON response
            try:
                # Clean response - remove markdown code blocks if present
                cleaned_response = gemini_response.strip()
                
                # Handle various markdown formats
                if "```json" in cleaned_response:
                    # Extract JSON between ```json and ```
                    start = cleaned_response.find("```json") + 7
                    end = cleaned_response.find("```", start)
                    if end > start:
                        cleaned_response = cleaned_response[start:end].strip()
                elif "```" in cleaned_response:
                    # Extract content between first ``` and last ```
                    parts = cleaned_response.split("```")
                    if len(parts) >= 3:
                        cleaned_response = parts[1].strip()
                
                logger.info(f"Cleaned response preview: {cleaned_response[:200]}...")
                
                topics_data = json.loads(cleaned_response)
                if not isinstance(topics_data, list):
                    # If response is not a list, try to extract topics from nested structure
                    if isinstance(topics_data, dict) and 'topics' in topics_data:
                        topics_data = topics_data['topics']
                    elif isinstance(topics_data, dict) and 'items' in topics_data:
                        topics_data = topics_data['items']
                    else:
                        raise ValueError("Expected list of topics from Gemini API")
                        
                # Validate that we have a list of topics
                if not isinstance(topics_data, list):
                    raise ValueError("Expected list of topics from Gemini API")
                
                logger.info(f"Successfully parsed {len(topics_data)} topics from Gemini response")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse Gemini response as JSON or invalid format: {e}")
                logger.error(f"Raw Gemini response: {gemini_response[:500]}...")
                # Fallback: create some default topics based on brief
                logger.warning("Using fallback topics generation based on brief content")
                topics_data = _generate_fallback_topics(topics_to_generate, super_context)
            
            # Save topics to database
            saved_topics = []
            for topic_data in topics_data:
                if isinstance(topic_data, dict) and "title" in topic_data and "description" in topic_data:
                    # Create SuggestedTopic
                    topic = models.SuggestedTopic(
                        title=topic_data["title"],
                        description=topic_data["description"],
                        category="blog",  # Default category for blog topics
                        content_plan_id=plan_id,  # Changed from organization_id to content_plan_id
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(topic)
                    saved_topics.append({
                        "title": topic_data["title"],
                        "description": topic_data["description"]
                    })
            
            db.commit()
            logger.info(f"Saved {len(saved_topics)} topics to database")
            
            # Update ContentPlan status
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if content_plan:
                content_plan.status = 'pending_blog_topic_approval'
                content_plan.updated_at = datetime.utcnow()
                db.commit()
                logger.info(f"Updated ContentPlan {plan_id} status to 'pending_blog_topic_approval'")
            
            return {
                "status": "SUCCESS",
                "plan_id": plan_id,
                "topics_generated": len(saved_topics),
                "topics": saved_topics,
                "message": f"Successfully generated {len(saved_topics)} blog topics"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in generate_and_save_blog_topics_task: {str(e)}")
        
        # Update plan status to error state
        try:
            db = SessionLocal()
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if content_plan:
                content_plan.status = 'error'
                content_plan.updated_at = datetime.utcnow()
                db.commit()
            db.close()
        except:
            pass
        
        self.retry(countdown=120, max_retries=2)


def _enhance_context_with_research(super_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Enhance super-context with additional research data using Tavily.
    
    Args:
        super_context: Base context from database
        
    Returns:
        Enhanced context with research data
    """
    try:
        # Use new ContentResearchOrchestrator
        import asyncio
        research_orchestrator = ContentResearchOrchestrator()
        
        # Run async research in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            # Extract organization context for research
            org_context = super_context.get("organization", {})
            
            # Get industry and key topics from briefs
            industry = org_context.get("industry", "general")
            key_topics = super_context.get("brief_insights", {}).get("key_topics", [])
            mandatory_topics = super_context.get("brief_insights", {}).get("mandatory_topics", [])
            
            # Research each mandatory topic using Gemini-generated queries
            research_results = {}
            
            # Get database session for prompt manager
            db = SessionLocal()
            try:
                prompt_manager = PromptManager(db)
                ai_config = AIConfigService(db)
                
                # Get Tavily query generation prompt
                tavily_prompt = prompt_manager._get_cached_prompt("generate_tavily_queries")
                tavily_model = ai_config._get_cached_model("generate_tavily_queries")
                
                if tavily_prompt:
                    # Generate queries for each mandatory topic
                    for topic in mandatory_topics[:3]:  # Limit to top 3 topics
                        # Generate Tavily queries using Gemini
                        query_prompt = tavily_prompt.format(
                            topic=topic,
                            industry=industry,
                            purpose="znajdowanie aktualnych informacji do tworzenia treści blogowych",
                            current_year=datetime.now().year
                        )
                        
                        queries_response = _call_gemini_api(query_prompt, tavily_model or "gemini-1.5-flash")
                        
                        if queries_response:
                            try:
                                # Clean the response if it contains markdown
                                cleaned_response = queries_response.strip()
                                if cleaned_response.startswith("```json"):
                                    cleaned_response = cleaned_response[7:]
                                if cleaned_response.startswith("```"):
                                    cleaned_response = cleaned_response[3:]
                                if cleaned_response.endswith("```"):
                                    cleaned_response = cleaned_response[:-3]
                                
                                search_queries = json.loads(cleaned_response.strip())
                                
                                # Perform research with generated queries
                                topic_research = loop.run_until_complete(
                                    research_orchestrator.research_topic(
                                        topic=topic,
                                        context=org_context,
                                        num_queries=len(search_queries)
                                    )
                                )
                                
                                # Add generated queries to research data
                                topic_research["generated_queries"] = search_queries
                                research_results[topic] = topic_research
                                
                            except json.JSONDecodeError:
                                logger.warning(f"Failed to parse Tavily queries for topic: {topic}")
                                # Fallback to standard research
                                research_data = loop.run_until_complete(
                                    research_orchestrator.comprehensive_research(
                                        topic=topic,
                                        organization_context=org_context,
                                        research_depth="deep"
                                    )
                                )
                                research_results[topic] = research_data
                        else:
                            # Fallback to standard research
                            research_data = loop.run_until_complete(
                                research_orchestrator.comprehensive_research(
                                    topic=topic,
                                    organization_context=org_context,
                                    research_depth="deep"
                                )
                            )
                            research_results[topic] = research_data
                else:
                    # No Tavily prompt found, use standard research
                    for topic in mandatory_topics[:3]:
                        research_data = loop.run_until_complete(
                            research_orchestrator.comprehensive_research(
                                topic=topic,
                                organization_context=org_context,
                                research_depth="deep"
                            )
                        )
                        research_results[topic] = research_data
                
                # Generate queries for industry trends
                if tavily_prompt:
                    industry_query_prompt = tavily_prompt.format(
                        topic=f"{industry} branża",
                        industry=industry,
                        purpose="poznanie najnowszych trendów i innowacji w branży",
                        current_year=datetime.now().year
                    )
                    
                    industry_queries_response = _call_gemini_api(industry_query_prompt, tavily_model or "gemini-1.5-flash")
                    
                    if industry_queries_response:
                        try:
                            # Clean the response
                            cleaned_response = industry_queries_response.strip()
                            if cleaned_response.startswith("```json"):
                                cleaned_response = cleaned_response[7:]
                            if cleaned_response.startswith("```"):
                                cleaned_response = cleaned_response[3:]
                            if cleaned_response.endswith("```"):
                                cleaned_response = cleaned_response[:-3]
                            
                            industry_queries = json.loads(cleaned_response.strip())
                            
                            # Research with generated queries
                            industry_research = loop.run_until_complete(
                                research_orchestrator.research_topic(
                                    topic=f"{industry} trends innovations",
                                    context=org_context,
                                    num_queries=len(industry_queries)
                                )
                            )
                            industry_research["generated_queries"] = industry_queries
                            research_results["industry_trends"] = industry_research
                            
                        except json.JSONDecodeError:
                            logger.warning("Failed to parse industry trend queries")
                            # Fallback
                            industry_research = loop.run_until_complete(
                                research_orchestrator.comprehensive_research(
                                    topic=f"{industry} trends innovations Poland {datetime.now().year}",
                                    organization_context=org_context,
                                    research_depth="deep"
                                )
                            )
                            research_results["industry_trends"] = industry_research
                    else:
                        # Fallback
                        industry_research = loop.run_until_complete(
                            research_orchestrator.comprehensive_research(
                                topic=f"{industry} trends innovations Poland {datetime.now().year}",
                                organization_context=org_context,
                                research_depth="deep"
                            )
                        )
                        research_results["industry_trends"] = industry_research
                else:
                    # No Tavily prompt, use standard approach
                    industry_research = loop.run_until_complete(
                        research_orchestrator.comprehensive_research(
                            topic=f"{industry} trends innovations Poland {datetime.now().year}",
                            organization_context=org_context,
                            research_depth="deep"
                        )
                    )
                    research_results["industry_trends"] = industry_research
                    
            finally:
                db.close()
            
        finally:
            loop.close()
        
        # Add research to context
        enhanced_context = super_context.copy()
        enhanced_context["research_data"] = research_results
        
        # Extract key insights for AI
        ai_insights = []
        for topic, data in research_results.items():
            if "synthesis" in data:
                synthesis = data["synthesis"]
                ai_insights.extend(synthesis.get("key_findings", []))
                ai_insights.extend([item["inspiration"] for item in synthesis.get("content_opportunities", [])])
        
        enhanced_context["ai_research_insights"] = ai_insights[:10]  # Top 10 insights
        
        logger.info("Successfully enhanced context with Tavily research")
        return enhanced_context
        
    except ImportError:
        logger.warning("Research integration module not available, using fallback")
    except Exception as e:
        logger.error(f"Research enhancement failed: {e}, using fallback")
    
    # Fallback to placeholder data if research fails
    enhanced_context = super_context.copy()
    
    # Add placeholder research data
    enhanced_context["research_data"] = {
        "industry_trends": [
            "AI and automation are transforming the industry",
            "Sustainability is becoming a key focus area",
            "Digital transformation continues to accelerate"
        ],
        "competitor_insights": [
            "Competitors are focusing on customer experience",
            "Content marketing is becoming more personalized",
            "Video content is gaining popularity"
        ],
        "market_opportunities": [
            "Growing demand for expert insights",
            "Increasing interest in thought leadership content",
            "Opportunities in emerging market segments"
        ]
    }
    
    return enhanced_context


def _generate_fallback_topics(topics_count: int, super_context: Dict[str, Any]) -> List[Dict[str, str]]:
    """
    Generate fallback topics when Gemini API fails.
    Uses brief content intelligently to create relevant topics.
    
    Args:
        topics_count: Number of topics to generate
        super_context: Context data for topic generation
        
    Returns:
        List of fallback topics
    """
    organization_name = super_context.get("organization", {}).get("name", "Your Company")
    industry = super_context.get("organization", {}).get("industry", "business")
    
    fallback_topics = []
    
    # First, add topics based on mandatory topics from briefs
    brief_insights = super_context.get("brief_insights", {})
    mandatory_topics = brief_insights.get("mandatory_topics", [])
    content_instructions = brief_insights.get("content_instructions", [])
    company_news = brief_insights.get("company_news", [])
    key_messages = brief_insights.get("key_messages", [])
    priority_items = brief_insights.get("priority_items", [])
    
    logger.info(f"Generating fallback topics with: {len(mandatory_topics)} mandatory topics, {len(company_news)} company news")
    
    # 1. Create topics from mandatory topics (most important)
    for i, mandatory_topic in enumerate(mandatory_topics[:topics_count]):
        fallback_topics.append({
            "title": mandatory_topic,
            "description": f"Artykuł omawiający {mandatory_topic} z perspektywy {organization_name}. Kluczowy temat wymagany w briefie do realizacji."
        })
    
    # 2. If we still need more topics, use company news
    remaining_count = topics_count - len(fallback_topics)
    for i, news in enumerate(company_news[:remaining_count]):
        fallback_topics.append({
            "title": f"{news} - aktualności {organization_name}",
            "description": f"Artykuł przedstawiający {news}. Aktualne wydarzenie w firmie {organization_name}."
        })
    
    # 3. Use priority items
    remaining_count = topics_count - len(fallback_topics)
    for i, priority in enumerate(priority_items[:remaining_count]):
        fallback_topics.append({
            "title": f"{priority} - priorytet dla {industry}",
            "description": f"Szczegółowa analiza {priority} jako kluczowego obszaru dla branży {industry}."
        })
    
    # 4. Use key messages as topics
    remaining_count = topics_count - len(fallback_topics)
    for i, message in enumerate(key_messages[:remaining_count]):
        fallback_topics.append({
            "title": f"{message} w praktyce {organization_name}",
            "description": f"Jak {organization_name} realizuje {message} w codziennej działalności."
        })
    
    # 5. If we STILL need more topics, use intelligent templates based on brief
    remaining_count = topics_count - len(fallback_topics)
    if remaining_count > 0:
        # Generate templates based on brief content
        has_energy_topics = any("energi" in str(t).lower() for t in mandatory_topics)
        has_safety_topics = any("bezpiecz" in str(t).lower() or "ochrona" in str(t).lower() for t in mandatory_topics)
        has_tech_topics = any("system" in str(t).lower() or "technolog" in str(t).lower() for t in mandatory_topics)
        
        topic_templates = []
        
        if has_energy_topics:
            topic_templates.extend([
                f"Optymalizacja zużycia energii w {industry} - case study {organization_name}",
                f"Monitoring energetyczny jako klucz do efektywności w {industry}",
                f"Zrównoważone zarządzanie energią w dużych zakładach przemysłowych"
            ])
        
        if has_safety_topics:
            topic_templates.extend([
                f"Nowoczesne systemy bezpieczeństwa w {industry}",
                f"Ochrona przeciwpożarowa w erze technologii - perspektywa {organization_name}",
                f"Symulacje CFD w projektowaniu systemów bezpieczeństwa"
            ])
        
        if has_tech_topics:
            topic_templates.extend([
                f"Integracja systemów w {industry} - doświadczenia {organization_name}",
                f"Automatyzacja procesów jako przewaga konkurencyjna",
                f"Innowacyjne rozwiązania technologiczne dla {industry}"
            ])
        
        # Add generic templates if needed
        if len(topic_templates) < remaining_count:
            topic_templates.extend([
                f"Jak {organization_name} wykorzystuje nowoczesne technologie w {industry}",
                f"Trendy w {industry} na 2025 rok według ekspertów {organization_name}",
                f"Najlepsze praktyki w {industry} - poradnik {organization_name}"
            ])
        
        for i in range(min(remaining_count, len(topic_templates))):
            fallback_topics.append({
                "title": topic_templates[i],
                "description": f"Artykuł ekspercki przygotowany przez {organization_name}, omawiający kluczowe aspekty tematu."
            })
    
    logger.info(f"Generated {len(fallback_topics)} fallback topics based on brief content")
    return fallback_topics 


@shared_task(bind=True, name="content_gen.generate_correlated_sm_variants_task")
def generate_correlated_sm_variants_task(self, plan_id: int) -> List[int]:
    """
    Task 3: Generate correlated social media variants based on approved blog topics.
    
    Retrieves all approved blog topics for the plan and generates SM variants
    that are correlated with the blog content.
    
    Args:
        plan_id: ID of the ContentPlan to process
        
    Returns:
        List of ContentVariant IDs (both blog and SM) ready for scheduling
    """
    logger.info(f"Starting generate_correlated_sm_variants_task for plan_id: {plan_id}")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Get ContentPlan
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if not content_plan:
                raise ValueError(f"ContentPlan with ID {plan_id} not found")
            
            logger.info(f"Found ContentPlan: {content_plan.plan_period}")
            
            # Get approved SuggestedTopics ONLY for THIS content plan
            logger.info(f"Searching for approved topics for content plan {plan_id}")
            approved_topics = db.query(models.SuggestedTopic).filter(
                models.SuggestedTopic.content_plan_id == plan_id,
                models.SuggestedTopic.status == "approved",
                models.SuggestedTopic.category == "blog",  # Only blog topics
                models.SuggestedTopic.is_active == True
            ).all()
            logger.info(f"Found {len(approved_topics)} approved blog topics for plan {plan_id}")
            
            logger.info(f"Query returned {len(approved_topics) if approved_topics else 0} topics")
            if approved_topics:
                for topic in approved_topics:
                    logger.info(f"Found approved topic: {topic.title} (ID: {topic.id}, status: {topic.status})")
            
            if not approved_topics:
                logger.warning(f"No approved topics found for organization {content_plan.organization_id}")
                return []
            
            logger.info(f"Found {len(approved_topics)} approved topics")
            
            # Get organization and strategy context for SM generation
            organization = crud.organization_crud.get_by_id(db, content_plan.organization_id)
            
            # Get communication strategy
            strategies = db.query(models.CommunicationStrategy).filter(
                models.CommunicationStrategy.organization_id == content_plan.organization_id,
                models.CommunicationStrategy.is_active == True
            ).options(
                joinedload(models.CommunicationStrategy.platform_styles)
            ).order_by(models.CommunicationStrategy.created_at.desc()).limit(1).all()
            
            strategy = strategies[0] if strategies else None
            
            if not strategy:
                logger.warning(f"No active communication strategy found for organization {content_plan.organization_id}")
                raise ValueError("Communication strategy is required for SM correlation")
            
            # Get social media platforms from strategy
            try:
                sm_platforms = [ps for ps in strategy.platform_styles 
                              if ps.platform_name.lower() in ['facebook', 'instagram', 'linkedin', 'twitter', 'x']]
                logger.info(f"Found {len(sm_platforms)} social media platforms in strategy")
            except Exception as e:
                logger.error(f"Error accessing platform_styles: {e}")
                raise ValueError(f"Failed to access platform styles: {e}")
            
            if not sm_platforms:
                logger.warning("No social media platforms configured in strategy")
                raise ValueError("No social media platforms configured")
            
            # Get correlation rules
            from app.db.crud_content_brief import correlation_rule_crud
            rules = correlation_rule_crud.get_by_content_plan(db, plan_id)
            
            # Calculate SM distribution
            if rules:
                sm_posts_per_blog = rules.sm_posts_per_blog
                brief_based_posts = rules.brief_based_sm_posts
                standalone_posts = rules.standalone_sm_posts
                
                logger.info(f"Using custom correlation rules: {sm_posts_per_blog} per blog, "
                          f"{brief_based_posts} from briefs, {standalone_posts} standalone")
            else:
                # Default behavior - properly calculate standalone posts
                total_sm_quota = content_plan.sm_posts_quota
                blog_topics_count = len(approved_topics)
                
                # Each blog should have at least 1 SM post
                sm_posts_per_blog = 1
                total_correlated_posts = blog_topics_count * sm_posts_per_blog
                
                # Calculate standalone posts as the remainder
                if total_correlated_posts < total_sm_quota:
                    standalone_posts = total_sm_quota - total_correlated_posts
                else:
                    # If we already have enough correlated posts, no standalone needed
                    standalone_posts = 0
                    # But we might need to increase posts per blog
                    if blog_topics_count > 0:
                        sm_posts_per_blog = total_sm_quota // blog_topics_count
                
                brief_based_posts = 0
                
                logger.info(f"Using default correlation: {sm_posts_per_blog} SM posts per blog topic, "
                          f"{standalone_posts} standalone posts (total SM quota: {total_sm_quota})")
            
            # Get AI prompt and model for SM generation
            prompt_manager = PromptManager(db)
            ai_config = AIConfigService(db)
            
            prompt_template = prompt_manager._get_cached_prompt("generate_sm_variants_from_blog_context")
            model_name = ai_config._get_cached_model("generate_sm_variants_from_blog_context")
            
            if not prompt_template:
                raise ValueError("AI prompt 'generate_sm_variants_from_blog_context' not found")
            
            if not model_name:
                raise ValueError("AI model assignment 'generate_sm_variants_from_blog_context' not found")
            
            all_variant_ids = []
            
            # Process each approved blog topic
            for topic in approved_topics:
                logger.info(f"Processing topic: {topic.title}")
                
                # First, generate blog variants for this topic if not already done
                # Check if blog variants already exist
                existing_drafts = db.query(models.ContentDraft).filter(
                    models.ContentDraft.suggested_topic_id == topic.id,
                    models.ContentDraft.is_active == True
                ).all()
                
                blog_variant_ids = []
                if existing_drafts:
                    # Get existing blog variant IDs
                    for draft in existing_drafts:
                        blog_variants = crud.content_variant_crud.get_by_content_draft_id(db, draft.id)
                        blog_variant_ids.extend([v.id for v in blog_variants if v.status == "approved"])
                else:
                    # Generate blog variants
                    blog_result = generate_all_variants_for_topic_task(topic.id)
                    if blog_result.get("success"):
                        draft_id = blog_result.get("content_draft_id")
                        if draft_id:
                            blog_variants = crud.content_variant_crud.get_by_content_draft_id(db, draft_id)
                            blog_variant_ids.extend([v.id for v in blog_variants])
                
                all_variant_ids.extend(blog_variant_ids)
                
                # Generate correlated SM topics using AI
                formatted_prompt = prompt_template.format(
                    sm_posts_per_blog=sm_posts_per_blog,
                    blog_topic_title=topic.title,
                    blog_topic_description=topic.description or ""
                )
                
                # Add temporal context
                from app.tasks.variant_generation import get_temporal_context
                temporal_context = get_temporal_context()
                formatted_prompt += f"\n\n{temporal_context}"
                formatted_prompt += "\n\nPAMIĘTAJ: NIE wspominaj o porze roku. Kontekst czasowy to tylko wskazówka aby uniknąć nieaktualnych tematów."
                
                logger.info("Calling Gemini API for SM topics generation")
                
                # Call Gemini API
                gemini_response = _call_gemini_api(formatted_prompt, model_name)
                
                if not gemini_response:
                    logger.warning(f"Failed to generate SM topics for blog topic {topic.id}")
                    continue
                
                # Parse JSON response
                try:
                    # Clean the response if it contains markdown code blocks
                    cleaned_response = gemini_response.strip()
                    if cleaned_response.startswith("```json"):
                        cleaned_response = cleaned_response[7:]  # Remove ```json
                    if cleaned_response.startswith("```"):
                        cleaned_response = cleaned_response[3:]  # Remove ```
                    if cleaned_response.endswith("```"):
                        cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                    cleaned_response = cleaned_response.strip()
                    
                    logger.info(f"Cleaned SM response preview: {cleaned_response[:200]}...")
                    
                    sm_topics_data = json.loads(cleaned_response)
                    if not isinstance(sm_topics_data, list):
                        logger.warning(f"Invalid SM topics response format for topic {topic.id}")
                        logger.warning(f"Expected list, got: {type(sm_topics_data)}")
                        continue
                        
                except (json.JSONDecodeError, ValueError) as e:
                    logger.error(f"Failed to parse SM topics response: {e}")
                    logger.error(f"Raw response: {gemini_response[:500]}...")
                    continue
                
                # Create SuggestedTopics for SM posts
                sm_topic_ids = []
                for sm_topic_data in sm_topics_data[:sm_posts_per_blog]:
                    if isinstance(sm_topic_data, dict) and "title" in sm_topic_data and "description" in sm_topic_data:
                        sm_topic = models.SuggestedTopic(
                            title=sm_topic_data["title"],
                            description=sm_topic_data["description"],
                            category="social_media",
                            content_plan_id=plan_id,
                            parent_topic_id=topic.id,  # Link to blog topic
                            status="approved",  # Auto-approve for automatic variant generation
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        
                        db.add(sm_topic)
                        db.flush()
                        sm_topic_ids.append(sm_topic.id)
                        
                        # Don't create draft here - variant generation task will create it
                        # This avoids duplicate drafts
                
                db.commit()
                logger.info(f"Created {len(sm_topic_ids)} SM topics for blog topic {topic.id}")
                
                # Generate variants for SM topics
                logger.info(f"Generating variants for {len(sm_topic_ids)} SM topics")
                for sm_topic_id in sm_topic_ids:
                    sm_result = generate_all_variants_for_topic_task(sm_topic_id)
                    if sm_result.get("success"):
                        sm_draft_id = sm_result.get("content_draft_id")
                        if sm_draft_id:
                            sm_variants = crud.content_variant_crud.get_by_content_draft_id(db, sm_draft_id)
                            all_variant_ids.extend([v.id for v in sm_variants])
                            logger.info(f"Generated {len(sm_variants)} variants for SM topic {sm_topic_id}")
            
            logger.info(f"Generated {len(all_variant_ids)} blog-correlated variants")
            
            # Generate brief-based SM posts if configured
            if brief_based_posts > 0:
                logger.info(f"Generating {brief_based_posts} brief-based SM posts")
                from app.tasks.brief_analysis import generate_brief_based_content_task
                
                brief_topic_ids = generate_brief_based_content_task(plan_id)
                
                # Generate variants for brief-based topics
                for topic_id in brief_topic_ids:
                    result = generate_all_variants_for_topic_task(topic_id)
                    if result.get("success"):
                        draft_id = result.get("content_draft_id")
                        if draft_id:
                            variants = crud.content_variant_crud.get_by_content_draft_id(db, draft_id)
                            all_variant_ids.extend([v.id for v in variants])
            
            # Generate standalone SM posts if configured
            if standalone_posts > 0:
                logger.info(f"Generating {standalone_posts} standalone SM posts")
                
                # Get organization context for standalone posts
                from app.tasks.website_analysis import get_website_analysis_for_organization
                website_analysis = get_website_analysis_for_organization(db, organization.id)
                
                org_context = {
                    "organization_name": organization.name,
                    "industry": website_analysis.get('industry') if website_analysis else organization.industry or "",
                    "general_style": strategy.general_style if strategy else None,
                    "website_analysis": website_analysis if website_analysis else None
                }
                
                # Generate standalone topics
                standalone_topic_ids = _generate_standalone_sm_topics(
                    db, plan_id, standalone_posts, org_context, model_name
                )
                
                # Generate variants for standalone topics
                for topic_id in standalone_topic_ids:
                    result = generate_all_variants_for_topic_task(topic_id)
                    if result.get("success"):
                        draft_id = result.get("content_draft_id")
                        if draft_id:
                            variants = crud.content_variant_crud.get_by_content_draft_id(db, draft_id)
                            all_variant_ids.extend([v.id for v in variants])
            
            logger.info(f"Generated total of {len(all_variant_ids)} variants (all types)")
            
            # Update ContentPlan status
            content_plan.status = 'pending_final_scheduling'
            content_plan.updated_at = datetime.utcnow()
            db.commit()
            
            return all_variant_ids
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in generate_correlated_sm_variants_task: {str(e)}")
        
        # Update plan status to error state
        try:
            db = SessionLocal()
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if content_plan:
                content_plan.status = 'error'
                content_plan.updated_at = datetime.utcnow()
                db.commit()
            db.close()
        except:
            pass
        
        self.retry(countdown=120, max_retries=2)


@shared_task(bind=True, name="content_gen.schedule_final_plan_task")
def schedule_final_plan_task(self, variant_ids: List[int], plan_id: int) -> Dict[str, Any]:
    """
    Task 4: Schedule all variants in calendar using AI-powered scheduling.
    
    Takes all generated variants and creates a publication schedule,
    then saves as ScheduledPost records.
    
    Args:
        variant_ids: List of ContentVariant IDs to schedule
        plan_id: ID of the ContentPlan
        
    Returns:
        Dict with scheduling results
    """
    logger.info(f"Starting schedule_final_plan_task for plan_id: {plan_id} with {len(variant_ids)} variants")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Get ContentPlan
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if not content_plan:
                raise ValueError(f"ContentPlan with ID {plan_id} not found")
            
            if not variant_ids:
                logger.warning("No variants to schedule")
                return {"status": "SUCCESS", "scheduled_posts": 0, "message": "No variants to schedule"}
            
            # Get all ContentVariants
            variants = []
            for variant_id in variant_ids:
                variant = crud.content_variant_crud.get_by_id(db, variant_id)
                if variant:
                    variants.append(variant)
            
            if not variants:
                logger.warning("No valid variants found")
                return {"status": "SUCCESS", "scheduled_posts": 0, "message": "No valid variants found"}
            
            logger.info(f"Found {len(variants)} valid variants to schedule")
            
            # Get AI prompt and model for scheduling
            prompt_manager = PromptManager(db)
            ai_config = AIConfigService(db)
            
            prompt_template = prompt_manager._get_cached_prompt("schedule_topics")
            model_name = ai_config._get_cached_model("schedule_topics")
            
            if not prompt_template:
                raise ValueError("AI prompt 'schedule_topics' not found")
            
            if not model_name:
                raise ValueError("AI model assignment 'schedule_topics' not found")
            
            # Prepare variants list for AI
            variants_list = []
            for variant in variants:
                # Get the associated draft and topic for context
                draft = crud.content_draft_crud.get_by_id(db, variant.content_draft_id)
                topic = None
                if draft:
                    topic = crud.suggested_topic_crud.get_by_id(db, draft.suggested_topic_id)
                
                variant_info = {
                    "content_variant_id": variant.id,
                    "platform_name": variant.platform_name,
                    "content_preview": variant.content_text[:100] + "..." if len(variant.content_text) > 100 else variant.content_text,
                    "topic_title": topic.title if topic else "Unknown",
                    "topic_category": topic.category if topic else "unknown"
                }
                variants_list.append(variant_info)
            
            # Format variants list as JSON for AI
            variants_json = json.dumps(variants_list, ensure_ascii=False, indent=2)
            
            # Get scheduling preferences or use defaults
            scheduling_preferences = content_plan.scheduling_preferences or """
Zasady harmonogramu:
1. Publikuj treści blogowe w dni robocze (poniedziałek-piątek) między 9:00-17:00
2. Publikuj posty social media codziennie między 8:00-20:00
3. Zachowaj odstęp minimum 2 godzin między publikacjami
4. Posty zapowiadające powinny być publikowane przed artykułami głównymi
5. Równomiernie rozłóż publikacje w całym okresie planu
"""
            
            # Format prompt with context
            final_prompt = prompt_template.format(
                plan_period=content_plan.plan_period,
                variants_list=variants_json,
                scheduling_preferences=scheduling_preferences
            )
            
            logger.info("Calling Gemini API for scheduling generation")
            
            # Call Gemini API
            gemini_response = _call_gemini_api(final_prompt, model_name)
            
            if not gemini_response:
                raise ValueError("Gemini API returned empty response for scheduling")
            
            # Parse JSON response
            try:
                # Clean the response if it contains markdown code blocks
                cleaned_response = gemini_response.strip()
                if cleaned_response.startswith("```json"):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith("```"):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith("```"):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                
                schedule_data = json.loads(cleaned_response)
                if not isinstance(schedule_data, list):
                    raise ValueError("Expected list of scheduled items from Gemini API")
                    
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"Failed to parse scheduling response: {e}")
                logger.error(f"Raw Gemini response: {gemini_response[:500]}...")
                raise ValueError("Failed to parse AI scheduling response")
            
            # Create ScheduledPost records
            scheduled_posts = []
            for schedule_item in schedule_data:
                if (isinstance(schedule_item, dict) and 
                    "content_variant_id" in schedule_item and 
                    "publication_date" in schedule_item):
                    
                    try:
                        # Parse publication date
                        from datetime import datetime
                        pub_date = datetime.strptime(schedule_item["publication_date"], "%Y-%m-%d %H:%M")
                        
                        # Find the variant
                        variant_id = schedule_item["content_variant_id"]
                        variant = next((v for v in variants if v.id == variant_id), None)
                        
                        if variant:
                            # Get topic info for post title
                            draft = crud.content_draft_crud.get_by_id(db, variant.content_draft_id)
                            topic = None
                            if draft:
                                topic = crud.suggested_topic_crud.get_by_id(db, draft.suggested_topic_id)
                            
                            # Create ScheduledPost
                            scheduled_post = models.ScheduledPost(
                                publication_date=pub_date,
                                status='scheduled',
                                post_type=topic.category if topic else 'content',
                                title=topic.title if topic else 'Generated Content',
                                content_plan_id=plan_id,
                                content_variant_id=variant_id,
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            
                            db.add(scheduled_post)
                            scheduled_posts.append({
                                "variant_id": variant_id,
                                "platform": variant.platform_name,
                                "publication_date": pub_date.isoformat(),
                                "title": topic.title if topic else 'Generated Content'
                            })
                        
                    except (ValueError, KeyError) as e:
                        logger.warning(f"Failed to process schedule item: {e}")
                        continue
            
            db.commit()
            logger.info(f"Created {len(scheduled_posts)} scheduled posts")
            
            # Update ContentPlan status to complete
            content_plan.status = 'complete'
            content_plan.updated_at = datetime.utcnow()
            db.commit()
            logger.info(f"Updated ContentPlan {plan_id} status to 'complete'")
            
            return {
                "status": "SUCCESS",
                "plan_id": plan_id,
                "scheduled_posts": len(scheduled_posts),
                "schedule": scheduled_posts,
                "message": f"Successfully scheduled {len(scheduled_posts)} posts for publication"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in schedule_final_plan_task: {str(e)}")
        
        # Update plan status to error state
        try:
            db = SessionLocal()
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if content_plan:
                content_plan.status = 'error'
                content_plan.updated_at = datetime.utcnow()
                db.commit()
            db.close()
        except:
            pass
        
        self.retry(countdown=120, max_retries=2)


def _generate_standalone_sm_topics(db: Session, plan_id: int, count: int, 
                                 org_context: Dict[str, Any], model_name: str) -> List[int]:
    """
    Generate standalone SM topics not related to blog posts
    
    Args:
        db: Database session
        plan_id: Content plan ID
        count: Number of topics to generate
        org_context: Organization context
        model_name: AI model to use
        
    Returns:
        List of generated topic IDs
    """
    logger.info(f"Generating {count} standalone SM topics")
    
    try:
        # Get prompt manager
        prompt_manager = PromptManager(db)
        
        prompt_template = prompt_manager._get_cached_prompt("generate_standalone_sm")
        if not prompt_template:
            prompt_template = """Generate {count} standalone social media post ideas for {organization_name} in the {industry} industry.

These should be engaging posts that are NOT related to any specific blog content, but rather:
- Company updates and news
- Industry insights and trends
- Tips and quick advice
- Engagement posts (questions, polls)
- Behind-the-scenes content
- Team highlights
- Customer success stories

Style: {style_info}

{website_context}

Return as JSON array with objects containing "title" and "description"."""
        
        # Format style info
        style_info = "Professional and engaging"
        if org_context.get("general_style"):
            style = org_context["general_style"]
            style_info = f"Tone: {getattr(style, 'tone', 'professional')}, Language: {getattr(style, 'language', 'polish')}"
        
        # Format website context
        website_context = ""
        if org_context.get("website_analysis"):
            wa = org_context["website_analysis"]
            website_parts = []
            
            if wa.get("services"):
                website_parts.append(f"Company services: {', '.join(wa['services'][:3])}")
            if wa.get("values"):
                website_parts.append(f"Company values: {', '.join(wa['values'][:3])}")
            if wa.get("target_audience"):
                website_parts.append(f"Target audience: {', '.join(wa['target_audience'])}")
            if wa.get("content_tone"):
                website_parts.append(f"Content tone: {wa['content_tone']}")
            if wa.get("key_topics"):
                website_parts.append(f"Key topics from website: {', '.join(wa['key_topics'][:5])}")
            
            if website_parts:
                website_context = "\nWebsite Analysis Context:\n" + "\n".join(website_parts)
        
        # Format prompt
        final_prompt = prompt_template.format(
            count=count,
            organization_name=org_context["organization_name"],
            industry=org_context["industry"] or "business",
            style_info=style_info,
            website_context=website_context
        )
        
        # Call AI
        ai_response = _call_gemini_api(final_prompt, model_name)
        
        generated_ids = []
        if ai_response:
            try:
                topics_data = json.loads(ai_response)
                
                for topic_data in topics_data[:count]:
                    if isinstance(topic_data, dict) and "title" in topic_data:
                        topic = models.SuggestedTopic(
                            title=topic_data["title"],
                            description=topic_data.get("description", ""),
                            category="social_media",
                            content_plan_id=plan_id,
                            status="approved",  # Auto-approve standalone
                            meta_data={"source": "standalone", "correlated": False},
                            is_active=True,
                            created_at=datetime.utcnow(),
                            updated_at=datetime.utcnow()
                        )
                        db.add(topic)
                        db.flush()
                        generated_ids.append(topic.id)
                        
                        # Don't create draft here - variant generation task will create it
                        # This avoids duplicate drafts
                
                db.commit()
                logger.info(f"Generated {len(generated_ids)} standalone topics")
                
            except (json.JSONDecodeError, Exception) as e:
                logger.error(f"Error processing standalone topics: {e}")
        
        return generated_ids
        
    except Exception as e:
        logger.error(f"Error in _generate_standalone_sm_topics: {e}")
        return [] 