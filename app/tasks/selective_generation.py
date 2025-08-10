"""
Selective content generation for approved topics only
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from celery import shared_task, group
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic, ContentPlan, ContentVariant, ContentDraft, PlatformStyle
from app.tasks.variant_generation import generate_all_variants_for_topic_task
from app.tasks.batch_generation import (
    group_topics_by_type, 
    should_use_batch_generation,
    generate_batch_prompt,
    process_batch_response,
    group_platforms_by_type
)
from app.core.platform_mapping import ContentType, get_platforms_for_topic_category, get_platform_type
from app.db import crud
from app.core.ai_config_service import AIConfigService
from app.core.prompt_manager import PromptManager

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="content_gen.generate_variants_for_approved_sm_topics")
def generate_variants_for_approved_sm_topics(self, content_plan_id: int) -> Dict[str, Any]:
    """
    Generate content variants only for approved SM topics
    
    This task is called when user manually approves SM topics
    and wants to generate their variants
    """
    logger.info(f"Starting variant generation for approved SM topics in plan {content_plan_id}")
    
    db = SessionLocal()
    try:
        # Get approved SM topics that don't have variants yet
        approved_sm_topics = db.query(SuggestedTopic).filter(
            SuggestedTopic.content_plan_id == content_plan_id,
            SuggestedTopic.category == "social_media",
            SuggestedTopic.status == "approved",
            SuggestedTopic.is_active == True
        ).all()
        
        # Filter out topics that already have content drafts
        topics_needing_variants = []
        for topic in approved_sm_topics:
            has_draft = db.query(ContentDraft).filter(
                ContentDraft.suggested_topic_id == topic.id,
                ContentDraft.is_active == True
            ).first() is not None
            
            if not has_draft:
                topics_needing_variants.append(topic)
        
        if not topics_needing_variants:
            logger.info("No approved SM topics need variant generation")
            return {
                "status": "SUCCESS",
                "message": "No topics to process",
                "topics_processed": 0
            }
        
        logger.info(f"Found {len(topics_needing_variants)} approved SM topics needing variants")
        
        # Get communication strategy
        content_plan = db.query(ContentPlan).get(content_plan_id)
        if not content_plan:
            raise ValueError(f"Content plan {content_plan_id} not found")
        
        strategy = crud.communication_strategy_crud.get_by_organization_id(
            db, content_plan.organization_id
        )
        
        if not strategy:
            raise ValueError("No communication strategy found")
        
        # Filter platforms for social media only
        sm_platforms = [
            ps for ps in strategy.platform_styles
            if get_platform_type(ps.platform_name) == ContentType.SOCIAL_MEDIA
        ]
        
        if not sm_platforms:
            logger.warning("No social media platforms configured")
            return {
                "status": "SUCCESS",
                "message": "No SM platforms configured",
                "topics_processed": 0
            }
        
        # Group topics for potential batch processing
        topic_groups = group_topics_by_type(topics_needing_variants)
        
        total_variants_created = 0
        total_topics_processed = 0
        
        # Process each group
        for category, topics in topic_groups.items():
            if should_use_batch_generation(len(topics), len(sm_platforms)):
                # Use batch generation
                logger.info(f"Using batch generation for {len(topics)} {category} topics")
                
                variants_created = _batch_generate_variants(
                    topics, sm_platforms, strategy, db
                )
                total_variants_created += variants_created
                total_topics_processed += len(topics)
            else:
                # Use individual generation
                logger.info(f"Using individual generation for {len(topics)} {category} topics")
                
                for topic in topics:
                    result = generate_all_variants_for_topic_task(topic.id)
                    if result.get("success"):
                        total_variants_created += result.get("variants_created", 0)
                        total_topics_processed += 1
        
        return {
            "status": "SUCCESS",
            "topics_processed": total_topics_processed,
            "variants_created": total_variants_created,
            "message": f"Generated {total_variants_created} variants for {total_topics_processed} topics"
        }
        
    except Exception as e:
        logger.error(f"Error in generate_variants_for_approved_sm_topics: {str(e)}")
        return {
            "status": "FAILED",
            "error": str(e)
        }
    finally:
        db.close()


def _batch_generate_variants(
    topics: List[SuggestedTopic],
    platforms: List[PlatformStyle],
    strategy: Any,
    db: Session
) -> int:
    """Generate variants for multiple topics in a single AI call"""
    
    try:
        # Get AI configuration
        prompt_manager = PromptManager(db)
        ai_config = AIConfigService(db)
        
        # Get prompt template
        prompt_template = prompt_manager._get_cached_prompt("generate_single_variant")
        if not prompt_template:
            logger.error("No prompt template found for variant generation")
            return 0
        
        model_name = ai_config._get_cached_model("generate_single_variant")
        if not model_name:
            model_name = "gemini-1.5-pro-latest"
        
        # Get general context
        from app.tasks.variant_generation import get_general_strategy_context
        general_context = get_general_strategy_context(strategy)
        
        # Create topic and platform maps
        topics_map = {topic.id: topic for topic in topics}
        platforms_map = {ps.platform_name: ps for ps in platforms}
        
        # Generate batch prompt
        batch_prompt = generate_batch_prompt(
            topics, platforms, prompt_template, general_context
        )
        
        # Call AI
        from app.tasks.variant_generation import _call_gemini_api
        response = _call_gemini_api(batch_prompt, model_name)
        
        if not response:
            logger.error("No response from AI for batch generation")
            return 0
        
        # Process response
        variants, success_count, failed_count = process_batch_response(
            response, topics_map, platforms_map, db
        )
        
        db.commit()
        
        logger.info(f"Batch generation complete: {success_count} variants created, {failed_count} failed")
        return success_count
        
    except Exception as e:
        logger.error(f"Error in batch variant generation: {str(e)}")
        db.rollback()
        return 0


@shared_task(bind=True, name="content_gen.generate_single_topic_variants")
def generate_single_topic_variants(self, topic_id: int, platform_names: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Generate variants for a single topic, optionally for specific platforms only
    
    Args:
        topic_id: ID of the topic
        platform_names: Optional list of platform names to generate for
    """
    logger.info(f"Generating variants for topic {topic_id}, platforms: {platform_names}")
    
    if platform_names:
        # TODO: Implement platform-specific generation
        # For now, fall back to all platforms
        pass
    
    return generate_all_variants_for_topic_task(topic_id)