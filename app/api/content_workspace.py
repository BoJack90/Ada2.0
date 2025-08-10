"""
Content workspace API endpoints for managing drafts and variants
"""

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db import crud, models
from app.core.dependencies import get_current_active_user
from app.db.models import User
from app.db.schemas import ContentDraftWithDetails, ContentVariantDetail

router = APIRouter()


@router.get("/content-plans/{plan_id}/drafts", response_model=List[ContentDraftWithDetails])
async def get_plan_drafts(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all content drafts for a specific content plan with full details.
    
    Returns drafts with:
    - Topic information (title, category, parent relationship)
    - Variants with platform information
    - Content plan details
    """
    
    # Get content plan first
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content plan not found"
        )
    
    # Check access
    if not crud.organization_crud.user_has_access(db, content_plan.organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Get all drafts for this plan with relationships
    drafts = db.query(models.ContentDraft).join(
        models.SuggestedTopic
    ).options(
        joinedload(models.ContentDraft.suggested_topic).joinedload(models.SuggestedTopic.parent),
        joinedload(models.ContentDraft.suggested_topic).joinedload(models.SuggestedTopic.content_plan),
        joinedload(models.ContentDraft.variants)
    ).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.ContentDraft.is_active == True
    ).all()
    
    # Transform to detailed response
    result = []
    for draft in drafts:
        topic = draft.suggested_topic
        
        # Prepare variant details
        variant_details = []
        for variant in draft.variants:
            variant_details.append({
                "id": variant.id,
                "platform_name": variant.platform_name,
                "status": variant.status,
                "content_preview": variant.content_text[:200] + "..." if len(variant.content_text) > 200 else variant.content_text,
                "created_at": variant.created_at
            })
        
        # Determine if this is correlated content
        is_correlated = topic.parent_topic_id is not None
        parent_topic_title = None
        if is_correlated and topic.parent:
            parent_topic_title = topic.parent.title
        
        draft_detail = {
            "id": draft.id,
            "suggested_topic": {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "category": topic.category,
                "is_correlated": is_correlated,
                "parent_topic_title": parent_topic_title
            },
            "status": draft.status,
            "variants": variant_details,
            "variants_count": len(variant_details),
            "content_plan": {
                "id": content_plan.id,
                "plan_period": content_plan.plan_period
            },
            "created_at": draft.created_at,
            "updated_at": draft.updated_at
        }
        
        result.append(draft_detail)
    
    # Sort by creation date, newest first
    result.sort(key=lambda x: x["created_at"], reverse=True)
    
    return result


@router.get("/content-workspace/all-drafts")
async def get_all_drafts(
    organization_id: int,
    plan_id: Optional[int] = None,
    category: Optional[str] = None,
    platform: Optional[str] = None,
    is_correlated: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all drafts across all plans with filtering options.
    
    Query parameters:
    - organization_id: Required - filter by organization
    - plan_id: Optional - filter by specific plan
    - category: Optional - filter by topic category (blog, social_media)
    - platform: Optional - filter by platform (requires joining with variants)
    - is_correlated: Optional - filter correlated/standalone content
    """
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Build query
    query = db.query(models.ContentDraft).join(
        models.SuggestedTopic
    ).join(
        models.ContentPlan
    ).options(
        joinedload(models.ContentDraft.suggested_topic).joinedload(models.SuggestedTopic.parent),
        joinedload(models.ContentDraft.suggested_topic).joinedload(models.SuggestedTopic.content_plan),
        joinedload(models.ContentDraft.variants)
    ).filter(
        models.ContentPlan.organization_id == organization_id,
        models.ContentDraft.is_active == True
    )
    
    # Apply filters
    if plan_id:
        query = query.filter(models.SuggestedTopic.content_plan_id == plan_id)
    
    if category:
        query = query.filter(models.SuggestedTopic.category == category)
    
    if is_correlated is not None:
        if is_correlated:
            query = query.filter(models.SuggestedTopic.parent_topic_id.isnot(None))
        else:
            query = query.filter(models.SuggestedTopic.parent_topic_id.is_(None))
    
    drafts = query.all()
    
    # Filter by platform if specified (post-query filtering)
    if platform:
        filtered_drafts = []
        for draft in drafts:
            has_platform = any(v.platform_name == platform for v in draft.variants)
            if has_platform:
                filtered_drafts.append(draft)
        drafts = filtered_drafts
    
    # Transform to response
    result = []
    for draft in drafts:
        topic = draft.suggested_topic
        plan = topic.content_plan
        
        # Group variants by platform
        platforms = {}
        for variant in draft.variants:
            if variant.platform_name not in platforms:
                platforms[variant.platform_name] = []
            platforms[variant.platform_name].append({
                "id": variant.id,
                "status": variant.status
            })
        
        # Determine correlation
        is_correlated = topic.parent_topic_id is not None
        parent_info = None
        if is_correlated and topic.parent:
            parent_info = {
                "id": topic.parent.id,
                "title": topic.parent.title,
                "category": topic.parent.category
            }
        
        # Extract source info from metadata
        source_info = None
        if topic.meta_data:
            source_info = {
                "type": topic.meta_data.get("source", "unknown"),
                "brief_based": topic.meta_data.get("brief_based", False),
                "correlated": topic.meta_data.get("correlated", is_correlated)
            }
        
        # Get platform details for SM posts
        suggested_platforms = []
        if topic.category == "social_media":
            # For SM, variants might have different platforms
            for platform_name, variants in platforms.items():
                suggested_platforms.append(platform_name)
        
        draft_summary = {
            "id": draft.id,
            "topic": {
                "id": topic.id,
                "title": topic.title,
                "category": topic.category,
                "is_correlated": is_correlated,
                "parent_topic": parent_info,
                "source_info": source_info,
                "suggested_platforms": suggested_platforms
            },
            "content_plan": {
                "id": plan.id,
                "plan_period": plan.plan_period,
                "status": plan.status
            },
            "status": draft.status,
            "platforms": platforms,
            "created_at": draft.created_at
        }
        
        result.append(draft_summary)
    
    # Sort by plan and creation date
    result.sort(key=lambda x: (x["content_plan"]["plan_period"], x["created_at"]), reverse=True)
    
    return {
        "total": len(result),
        "drafts": result,
        "filters_applied": {
            "organization_id": organization_id,
            "plan_id": plan_id,
            "category": category,
            "platform": platform,
            "is_correlated": is_correlated
        }
    }