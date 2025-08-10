"""
Batch content generation utilities for optimized AI calls
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from app.db.models import SuggestedTopic, ContentDraft, ContentVariant, PlatformStyle
from app.core.platform_mapping import get_platform_type, ContentType
from app.tasks.variant_generation import generate_content_with_ai, get_platform_rules
from celery import current_app

logger = logging.getLogger(__name__)


def group_topics_by_type(topics: List[SuggestedTopic]) -> Dict[str, List[SuggestedTopic]]:
    """Group topics by their category for batch processing"""
    groups = {}
    for topic in topics:
        category = topic.category or "general"
        if category not in groups:
            groups[category] = []
        groups[category].append(topic)
    return groups


def group_platforms_by_type(platforms: List[PlatformStyle]) -> Dict[ContentType, List[PlatformStyle]]:
    """Group platforms by their content type"""
    groups = {}
    for platform in platforms:
        platform_type = get_platform_type(platform.platform_name)
        if platform_type not in groups:
            groups[platform_type] = []
        groups[platform_type].append(platform)
    return groups


def generate_batch_prompt(
    topics: List[SuggestedTopic],
    platforms: List[PlatformStyle],
    prompt_template: str,
    general_context: str
) -> str:
    """Generate a batch prompt for multiple topics and platforms"""
    
    batch_instructions = """
You need to generate content variants for multiple topics and platforms in a single response.
Return your response as a JSON array with the following structure:

[
  {
    "topic_id": 123,
    "topic_title": "Title",
    "variants": [
      {
        "platform": "platform_name",
        "content": "Generated content for this platform"
      }
    ]
  }
]

IMPORTANT: Generate content for ALL topic-platform combinations listed below.
"""
    
    # Build topic-platform combinations
    combinations = []
    for topic in topics:
        topic_variants = []
        for platform in platforms:
            topic_variants.append({
                "platform": platform.platform_name,
                "rules": get_platform_rules(platform)
            })
        
        combinations.append({
            "topic_id": topic.id,
            "topic_title": topic.title,
            "topic_description": topic.description or "",
            "platforms": topic_variants
        })
    
    # Construct final prompt
    final_prompt = f"""
{batch_instructions}

General Context:
{general_context}

Topics and Platforms to Generate:
{json.dumps(combinations, indent=2)}

Base Instructions:
{prompt_template}

Remember to return ONLY a valid JSON array with all requested content variants.
"""
    
    return final_prompt


def process_batch_response(
    response: str,
    topics_map: Dict[int, SuggestedTopic],
    platforms_map: Dict[str, PlatformStyle],
    db: Session
) -> Tuple[List[ContentVariant], int, int]:
    """Process batch AI response and create content variants"""
    
    variants_created = []
    success_count = 0
    failed_count = 0
    
    try:
        # Parse JSON response
        batch_results = json.loads(response)
        
        if not isinstance(batch_results, list):
            logger.error("Batch response is not a list")
            return [], 0, len(topics_map) * len(platforms_map)
        
        # Process each topic result
        for topic_result in batch_results:
            if not isinstance(topic_result, dict):
                continue
                
            topic_id = topic_result.get("topic_id")
            if topic_id not in topics_map:
                logger.warning(f"Unknown topic ID in batch response: {topic_id}")
                continue
            
            topic = topics_map[topic_id]
            
            # Get or create ContentDraft for this topic
            content_draft = db.query(ContentDraft).filter(
                ContentDraft.suggested_topic_id == topic.id,
                ContentDraft.is_active == True
            ).first()
            
            if not content_draft:
                content_draft = ContentDraft(
                    suggested_topic_id=topic.id,
                    status="drafting",
                    created_by_task_id=current_app.current_task.request.id if hasattr(current_app, 'current_task') else None,
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(content_draft)
                db.flush()
            
            # Process variants for this topic
            variants = topic_result.get("variants", [])
            for variant_data in variants:
                if not isinstance(variant_data, dict):
                    continue
                
                platform_name = variant_data.get("platform")
                content = variant_data.get("content")
                
                if not platform_name or not content:
                    failed_count += 1
                    continue
                
                if platform_name not in platforms_map:
                    logger.warning(f"Unknown platform in batch response: {platform_name}")
                    failed_count += 1
                    continue
                
                # Create ContentVariant
                try:
                    content_variant = ContentVariant(
                        content_draft_id=content_draft.id,
                        platform_name=platform_name,
                        content_text=content,
                        status="pending_approval",
                        version=1,
                        created_by_task_id=current_app.current_task.request.id if hasattr(current_app, 'current_task') else None,
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    
                    db.add(content_variant)
                    variants_created.append(content_variant)
                    success_count += 1
                    
                except Exception as e:
                    logger.error(f"Error creating variant: {e}")
                    failed_count += 1
        
        # Update ContentDraft statuses
        draft_ids = set(v.content_draft_id for v in variants_created)
        for draft_id in draft_ids:
            draft = db.query(ContentDraft).get(draft_id)
            if draft:
                draft.status = "pending_approval"
                draft.updated_at = datetime.utcnow()
        
        db.flush()
        
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse batch response JSON: {e}")
        failed_count = len(topics_map) * len(platforms_map)
    except Exception as e:
        logger.error(f"Error processing batch response: {e}")
        failed_count = len(topics_map) * len(platforms_map)
    
    return variants_created, success_count, failed_count


def should_use_batch_generation(
    topics_count: int,
    platforms_count: int,
    estimated_tokens_per_item: int = 500
) -> bool:
    """Determine if batch generation would be more efficient"""
    
    # Estimate total tokens
    total_items = topics_count * platforms_count
    estimated_tokens = total_items * estimated_tokens_per_item
    
    # Use batch if:
    # 1. More than 5 total items
    # 2. Estimated tokens under 30k (to stay within model limits)
    # 3. Topics are of the same category
    
    return (
        total_items > 5 and 
        estimated_tokens < 30000 and
        topics_count <= 10  # Max 10 topics per batch
    )