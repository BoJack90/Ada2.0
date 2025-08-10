"""
Advanced Content Generation Tasks with Deep Reasoning

This module implements enhanced content generation using multi-agent approach,
deep reasoning, and comprehensive research integration.
"""

import json
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from celery import shared_task
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db import crud, models
from app.core.deep_reasoning import (
    DeepReasoningEngine, 
    EnhancedBriefAnalyzer,
    IndustryKnowledgeBase
)
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService
from app.tasks.content_generation import _call_gemini_api

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="content_gen.advanced_contextualize_task")
def advanced_contextualize_task(self, plan_id: int) -> Dict[str, Any]:
    """
    Enhanced contextualization with deep analysis and research
    """
    logger.info(f"Starting advanced contextualization for plan_id: {plan_id}")
    
    try:
        db = SessionLocal()
        
        try:
            # Get ContentPlan
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if not content_plan:
                raise ValueError(f"ContentPlan with ID {plan_id} not found")
            
            # Get Organization
            organization = crud.organization_crud.get_by_id(db, content_plan.organization_id)
            if not organization:
                raise ValueError(f"Organization not found")
            
            # Initialize knowledge base
            knowledge_base = IndustryKnowledgeBase(db)
            
            # Analyze company website if available
            company_analysis = {}
            if organization.website:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                company_analysis = loop.run_until_complete(
                    knowledge_base.analyze_company_website(organization.website)
                )
                loop.close()
            
            # Get industry insights
            industry = company_analysis.get("industry") or organization.industry or "business"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            industry_insights = loop.run_until_complete(
                knowledge_base.get_industry_insights(industry)
            )
            loop.close()
            
            # Get communication strategy with all related data
            strategy_data = _get_comprehensive_strategy(db, content_plan.organization_id)
            
            # Get and analyze briefs with enhanced analyzer
            brief_analyzer = EnhancedBriefAnalyzer(db)
            brief_insights = _analyze_all_briefs(db, plan_id, organization, brief_analyzer)
            
            # Get rejected topics for learning
            rejected_patterns = _analyze_rejected_topics(db, plan_id)
            
            # Build enhanced super-context
            super_context = {
                "organization": {
                    "name": organization.name,
                    "description": organization.description or "",
                    "industry": industry,
                    "website": organization.website or "",
                    "company_analysis": company_analysis
                },
                "content_plan": {
                    "plan_period": content_plan.plan_period,
                    "blog_posts_quota": content_plan.blog_posts_quota,
                    "sm_posts_quota": content_plan.sm_posts_quota,
                    "correlate_posts": content_plan.correlate_posts,
                    "scheduling_mode": content_plan.scheduling_mode,
                    "status": content_plan.status
                },
                "communication_strategy": strategy_data,
                "brief_insights": brief_insights,
                "industry_knowledge": industry_insights,
                "rejected_patterns": rejected_patterns,
                "generation_timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info("Successfully built enhanced super-context")
            
            return {
                "super_context": super_context,
                "plan_id": plan_id,
                "organization_id": content_plan.organization_id,
                "blog_posts_quota": content_plan.blog_posts_quota,
                "topics_to_generate": content_plan.blog_posts_quota + 3,
                "industry_identified": industry,
                "brief_count": brief_insights.get("total_briefs", 0)
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in advanced_contextualize_task: {str(e)}")
        self.retry(countdown=60, max_retries=3)


@shared_task(bind=True, name="content_gen.generate_topics_with_reasoning")
def generate_topics_with_reasoning_task(
    self, 
    context_data: Dict[str, Any], 
    plan_id: int
) -> Dict[str, Any]:
    """
    Generate topics using deep reasoning and multi-step approach
    """
    logger.info(f"Starting topic generation with reasoning for plan_id: {plan_id}")
    
    try:
        db = SessionLocal()
        
        try:
            # Initialize reasoning engine
            reasoning_engine = DeepReasoningEngine(db)
            
            # Extract context
            super_context = context_data["super_context"]
            topics_to_generate = context_data["topics_to_generate"]
            
            # Run deep reasoning analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            reasoning_result = loop.run_until_complete(
                reasoning_engine.analyze_with_reasoning(
                    super_context,
                    "generate_topics"
                )
            )
            loop.close()
            
            # Extract generated topics
            generated_topics = reasoning_result.get("result", [])
            
            if not generated_topics:
                logger.warning("Deep reasoning returned no topics, using fallback")
                generated_topics = _generate_intelligent_fallback_topics(
                    super_context, topics_to_generate
                )
            
            # Save topics to database with enhanced metadata
            saved_topics = []
            for topic_data in generated_topics[:topics_to_generate]:
                if isinstance(topic_data, dict) and "title" in topic_data:
                    # Create enhanced topic record
                    topic = models.SuggestedTopic(
                        title=topic_data["title"],
                        description=topic_data.get("description", ""),
                        category="blog",
                        content_plan_id=plan_id,
                        is_active=True,
                        meta_data={
                            "pillar": topic_data.get("pillar", "general"),
                            "brief_alignment": topic_data.get("brief_alignment", ""),
                            "unique_angle": topic_data.get("unique_angle", ""),
                            "target_keywords": topic_data.get("target_keywords", []),
                            "content_type": topic_data.get("content_type", "educational"),
                            "priority_score": topic_data.get("priority_score", 5),
                            "reasoning_steps": reasoning_result.get("reasoning_steps", {})
                        },
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(topic)
                    saved_topics.append({
                        "title": topic_data["title"],
                        "description": topic_data.get("description", ""),
                        "priority_score": topic_data.get("priority_score", 5),
                        "brief_alignment": topic_data.get("brief_alignment", "")
                    })
            
            db.commit()
            logger.info(f"Saved {len(saved_topics)} topics with reasoning metadata")
            
            # Update ContentPlan status
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if content_plan:
                content_plan.status = 'pending_blog_topic_approval'
                content_plan.updated_at = datetime.utcnow()
                db.commit()
            
            # Sort topics by priority for presentation
            saved_topics.sort(key=lambda x: x.get("priority_score", 0), reverse=True)
            
            return {
                "status": "SUCCESS",
                "plan_id": plan_id,
                "topics_generated": len(saved_topics),
                "topics": saved_topics,
                "reasoning_summary": {
                    "industry_insights_used": bool(
                        reasoning_result.get("reasoning_steps", {}).get("research")
                    ),
                    "brief_alignment_achieved": all(
                        t.get("brief_alignment") for t in saved_topics[:5]
                    ),
                    "diversity_score": _calculate_topic_diversity(saved_topics)
                },
                "message": f"Generated {len(saved_topics)} topics using deep reasoning"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in generate_topics_with_reasoning_task: {str(e)}")
        
        # Update plan status to error
        try:
            db = SessionLocal()
            content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
            if content_plan:
                content_plan.status = 'error'
                db.commit()
            db.close()
        except:
            pass
        
        self.retry(countdown=120, max_retries=2)


@shared_task(bind=True, name="content_gen.generate_smart_content_variants")
def generate_smart_content_variants_task(
    self, 
    topic_id: int,
    platform_name: str
) -> Dict[str, Any]:
    """
    Generate content variants with context awareness and optimization
    """
    logger.info(f"Generating smart variant for topic {topic_id}, platform {platform_name}")
    
    try:
        db = SessionLocal()
        
        try:
            # Get topic with metadata
            topic = db.query(models.SuggestedTopic).filter(
                models.SuggestedTopic.id == topic_id
            ).first()
            
            if not topic:
                raise ValueError(f"Topic {topic_id} not found")
            
            # Get content plan and organization context
            content_plan = crud.content_plan_crud.get_by_id(db, topic.content_plan_id)
            organization = crud.organization_crud.get_by_id(db, content_plan.organization_id)
            
            # Get strategy and platform style
            strategy = _get_comprehensive_strategy(db, organization.id)
            platform_style = next(
                (ps for ps in strategy.get("platform_styles", []) 
                 if ps["platform_name"].lower() == platform_name.lower()),
                None
            )
            
            # Build variant generation context
            variant_context = {
                "topic": {
                    "title": topic.title,
                    "description": topic.description,
                    "metadata": topic.metadata or {}
                },
                "platform": {
                    "name": platform_name,
                    "style": platform_style or {"style_description": "Professional and engaging"}
                },
                "organization": {
                    "name": organization.name,
                    "industry": organization.industry or "business"
                },
                "strategy": {
                    "tone": strategy.get("general_style", {}).get("tone", "professional"),
                    "cta_rules": strategy.get("cta_rules", []),
                    "forbidden_phrases": strategy.get("forbidden_phrases", []),
                    "preferred_phrases": strategy.get("preferred_phrases", [])
                }
            }
            
            # Generate using enhanced prompt
            prompt = _build_smart_variant_prompt(variant_context)
            model = AIConfigService(db)._get_cached_model("generate_single_variant") or "gemini-1.5-pro-latest"
            
            response = _call_gemini_api(prompt, model)
            
            if not response:
                raise ValueError("Failed to generate variant")
            
            # Parse and validate
            try:
                variant_data = json.loads(response)
            except:
                # Fallback to text extraction
                variant_data = {
                    "content": response,
                    "headline": topic.title,
                    "cta": "Dowiedz się więcej"
                }
            
            # Create or get ContentDraft
            draft = db.query(models.ContentDraft).filter(
                models.ContentDraft.suggested_topic_id == topic_id,
                models.ContentDraft.is_active == True
            ).first()
            
            if not draft:
                draft = models.ContentDraft(
                    suggested_topic_id=topic_id,
                    content_plan_id=topic.content_plan_id,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(draft)
                db.flush()
            
            # Create variant
            variant = models.ContentVariant(
                content_draft_id=draft.id,
                platform_name=platform_name,
                content_text=variant_data.get("content", ""),
                headline=variant_data.get("headline", topic.title),
                cta_text=variant_data.get("cta", ""),
                hashtags=json.dumps(variant_data.get("hashtags", [])),
                media_suggestions=json.dumps(variant_data.get("media_suggestions", [])),
                status="draft",
                meta_data={
                    "seo_keywords": variant_data.get("seo_keywords", []),
                    "readability_score": variant_data.get("readability_score", 0),
                    "generation_context": variant_context
                },
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(variant)
            db.commit()
            
            logger.info(f"Created smart variant for {platform_name}")
            
            return {
                "success": True,
                "variant_id": variant.id,
                "draft_id": draft.id,
                "platform": platform_name,
                "quality_metrics": {
                    "has_cta": bool(variant.cta_text),
                    "has_hashtags": bool(variant_data.get("hashtags")),
                    "seo_optimized": bool(variant_data.get("seo_keywords")),
                    "brand_aligned": True  # Assumed from strategy application
                }
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in generate_smart_content_variants_task: {str(e)}")
        return {"success": False, "error": str(e)}


# Helper functions

def _get_comprehensive_strategy(db: Session, organization_id: int) -> Dict[str, Any]:
    """Get complete communication strategy with all components"""
    strategies = db.query(models.CommunicationStrategy).filter(
        models.CommunicationStrategy.organization_id == organization_id,
        models.CommunicationStrategy.is_active == True
    ).order_by(models.CommunicationStrategy.created_at.desc()).limit(1).all()
    
    if not strategies:
        return _get_default_strategy()
    
    strategy = strategies[0]
    
    # Load all related data
    personas = db.query(models.Persona).filter(
        models.Persona.communication_strategy_id == strategy.id
    ).all()
    
    platform_styles = db.query(models.PlatformStyle).filter(
        models.PlatformStyle.communication_strategy_id == strategy.id
    ).all()
    
    general_style = db.query(models.GeneralStyle).filter(
        models.GeneralStyle.communication_strategy_id == strategy.id
    ).first()
    
    goals = db.query(models.CommunicationGoal).filter(
        models.CommunicationGoal.communication_strategy_id == strategy.id
    ).all()
    
    forbidden = db.query(models.ForbiddenPhrase).filter(
        models.ForbiddenPhrase.communication_strategy_id == strategy.id
    ).all()
    
    preferred = db.query(models.PreferredPhrase).filter(
        models.PreferredPhrase.communication_strategy_id == strategy.id
    ).all()
    
    cta_rules = db.query(models.CTARule).filter(
        models.CTARule.communication_strategy_id == strategy.id
    ).all()
    
    return {
        "strategy_name": strategy.name,
        "description": strategy.description or "",
        "communication_goals": [g.goal_text for g in goals],
        "target_audiences": [
            {
                "name": p.name, 
                "description": p.description,
                "age_range": p.age_range,
                "interests": p.interests
            } for p in personas
        ],
        "general_style": {
            "language": general_style.language if general_style else "polski",
            "tone": general_style.tone if general_style else "profesjonalny",
            "technical_content": general_style.technical_content if general_style else "accessible",
            "employer_branding_content": general_style.employer_branding_content if general_style else "expert"
        },
        "platform_styles": [
            {
                "platform_name": ps.platform_name,
                "length_description": ps.length_description,
                "style_description": ps.style_description,
                "notes": ps.notes or ""
            } for ps in platform_styles
        ],
        "forbidden_phrases": [fp.phrase for fp in forbidden],
        "preferred_phrases": [pp.phrase for pp in preferred],
        "cta_rules": [
            {
                "content_type": cta.content_type, 
                "cta_text": cta.cta_text
            } for cta in cta_rules
        ]
    }


def _get_default_strategy() -> Dict[str, Any]:
    """Return default strategy when none exists"""
    return {
        "strategy_name": "Default Strategy",
        "description": "Basic content strategy",
        "communication_goals": ["Increase brand awareness", "Educate audience"],
        "target_audiences": [{"name": "General", "description": "Broad audience"}],
        "general_style": {
            "language": "polski",
            "tone": "profesjonalny",
            "technical_content": "accessible",
            "employer_branding_content": "expert"
        },
        "platform_styles": [],
        "forbidden_phrases": [],
        "preferred_phrases": [],
        "cta_rules": []
    }


def _analyze_all_briefs(
    db: Session, 
    plan_id: int, 
    organization: Any,
    analyzer: EnhancedBriefAnalyzer
) -> Dict[str, Any]:
    """Analyze all briefs for a content plan"""
    from app.db.crud_content_brief import content_brief_crud
    
    briefs = content_brief_crud.get_by_content_plan(db, plan_id)
    
    if not briefs:
        return {
            "total_briefs": 0,
            "has_briefs": False,
            "key_topics": [],
            "priority_items": [],
            "important_context": []
        }
    
    combined_insights = {
        "total_briefs": len(briefs),
        "has_briefs": True,
        "key_topics": [],
        "priority_items": [],
        "important_context": [],
        "detailed_analysis": []
    }
    
    org_context = {
        "name": organization.name,
        "industry": organization.industry or "business",
        "website": organization.website or ""
    }
    
    for brief in briefs:
        if brief.extracted_content:
            # Run enhanced analysis
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            analysis = loop.run_until_complete(
                analyzer.analyze_brief(brief.extracted_content[:5000], org_context)
            )
            loop.close()
            
            # Aggregate insights
            if "core_topics" in analysis:
                combined_insights["key_topics"].extend(
                    analysis["core_topics"].get("main_themes", [])[:5]
                )
            
            if "priority_analysis" in analysis:
                combined_insights["priority_items"].extend(
                    analysis["priority_analysis"].get("explicitly_stated", [])[:3]
                )
            
            combined_insights["detailed_analysis"].append({
                "brief_id": brief.id,
                "title": brief.title,
                "priority_level": brief.priority_level,
                "analysis_summary": analysis
            })
    
    # Deduplicate
    combined_insights["key_topics"] = list(set(combined_insights["key_topics"]))[:20]
    combined_insights["priority_items"] = list(set(combined_insights["priority_items"]))[:10]
    
    return combined_insights


def _analyze_rejected_topics(db: Session, plan_id: int) -> Dict[str, Any]:
    """Analyze patterns in rejected topics"""
    rejected = db.query(models.SuggestedTopic).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.SuggestedTopic.status == 'rejected',
        models.SuggestedTopic.is_active == True
    ).all()
    
    if not rejected:
        return {"has_rejected": False, "patterns": []}
    
    # Analyze patterns
    rejected_titles = [t.title for t in rejected]
    rejected_descriptions = [t.description for t in rejected]
    
    analysis_prompt = f"""
Analyze these rejected topics to find patterns:

Rejected Titles:
{json.dumps(rejected_titles, ensure_ascii=False)}

Descriptions:
{json.dumps(rejected_descriptions, ensure_ascii=False)}

Identify:
1. Common themes in rejected topics
2. Style issues
3. Content type patterns
4. What to avoid in future

Return as JSON.
"""
    
    try:
        response = _call_gemini_api(analysis_prompt, "gemini-1.5-pro-latest")
        patterns = json.loads(response)
    except:
        patterns = {"themes": ["Unknown patterns"]}
    
    return {
        "has_rejected": True,
        "count": len(rejected),
        "patterns": patterns,
        "rejected_titles": rejected_titles[:10]
    }


def _generate_intelligent_fallback_topics(
    context: Dict[str, Any], 
    count: int
) -> List[Dict[str, Any]]:
    """Generate intelligent fallback topics when main generation fails"""
    org_name = context.get("organization", {}).get("name", "Firma")
    industry = context.get("organization", {}).get("industry", "biznes")
    brief_topics = context.get("brief_insights", {}).get("key_topics", [])
    
    # Use brief topics as inspiration
    topics = []
    templates = [
        "Jak {company} rewolucjonizuje {industry} poprzez {topic}",
        "Przewodnik po {topic} dla branży {industry}",
        "{topic}: Kluczowe trendy i prognozy na 2024",
        "Case study: Sukces {company} w obszarze {topic}",
        "Ekspert radzi: {topic} w praktyce biznesowej",
        "{industry} 4.0: Rola {topic} w transformacji cyfrowej",
        "Zrównoważony rozwój w {industry}: Znaczenie {topic}",
        "{topic} jako przewaga konkurencyjna w {industry}"
    ]
    
    for i in range(min(count, len(templates))):
        topic_focus = brief_topics[i % len(brief_topics)] if brief_topics else f"innowacje w {industry}"
        
        topics.append({
            "title": templates[i].format(
                company=org_name,
                industry=industry,
                topic=topic_focus
            ),
            "description": f"Kompleksowy artykuł ekspercki omawiający {topic_focus} z perspektywy {industry}.",
            "pillar": "thought_leadership",
            "priority_score": 7 - i * 0.5,
            "content_type": "educational"
        })
    
    return topics


def _calculate_topic_diversity(topics: List[Dict[str, Any]]) -> float:
    """Calculate diversity score for generated topics"""
    if not topics:
        return 0.0
    
    # Check title uniqueness
    titles = [t.get("title", "") for t in topics]
    unique_words = set()
    for title in titles:
        unique_words.update(title.lower().split())
    
    avg_words_per_title = sum(len(t.split()) for t in titles) / len(titles)
    diversity_score = len(unique_words) / (avg_words_per_title * len(titles))
    
    return min(1.0, diversity_score)


def _build_smart_variant_prompt(context: Dict[str, Any]) -> str:
    """Build intelligent prompt for variant generation"""
    topic = context["topic"]
    platform = context["platform"]
    organization = context["organization"]
    strategy = context["strategy"]
    
    prompt = f"""
Generate a high-quality content variant for {platform['name']}:

Topic: {topic['title']}
Description: {topic['description']}
Content Type: {topic['metadata'].get('content_type', 'educational')}
Brief Alignment: {topic['metadata'].get('brief_alignment', 'General topic')}
Unique Angle: {topic['metadata'].get('unique_angle', 'Expert perspective')}

Organization: {organization['name']} ({organization['industry']})
Tone: {strategy['tone']}

Platform Requirements:
{json.dumps(platform['style'], ensure_ascii=False, indent=2)}

Content Rules:
- MUST use preferred phrases: {json.dumps(strategy['preferred_phrases'], ensure_ascii=False)}
- MUST avoid forbidden phrases: {json.dumps(strategy['forbidden_phrases'], ensure_ascii=False)}
- Include appropriate CTA based on content type

For {platform['name']}, create:
1. Engaging headline (different from topic title)
2. Main content (formatted for platform)
3. Call-to-action
4. Hashtags (5-10 relevant ones)
5. Media suggestions
6. SEO keywords (for blog posts)

Make it:
- Highly engaging and valuable
- Platform-optimized
- SEO-friendly (if blog)
- Action-oriented
- Brief-aligned

Return as JSON with keys: headline, content, cta, hashtags, media_suggestions, seo_keywords, readability_score
"""
    
    return prompt