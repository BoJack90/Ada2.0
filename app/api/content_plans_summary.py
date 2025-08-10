"""
Content plans summary API endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
from datetime import datetime

from app.db.database import get_db
from app.db import crud, models
from app.core.dependencies import get_current_active_user
from app.db.models import User

router = APIRouter()


@router.get("/content-plans/summary")
async def get_content_plans_summary(
    organization_id: int = Query(..., description="Organization ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get summary of all content plans for an organization
    
    Returns plans with statistics about content generation
    """
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=403,
            detail="You don't have access to this organization"
        )
    
    # Build query
    query = db.query(models.ContentPlan).filter(
        models.ContentPlan.organization_id == organization_id,
        models.ContentPlan.is_active == True
    )
    
    if status and status != 'all':
        query = query.filter(models.ContentPlan.status == status)
    
    # Get plans
    plans = query.order_by(models.ContentPlan.created_at.desc()).all()
    
    # Build response with statistics
    result = []
    for plan in plans:
        # Get topic statistics
        topics_query = db.query(
            models.SuggestedTopic.category,
            models.SuggestedTopic.status,
            func.count(models.SuggestedTopic.id).label('count')
        ).filter(
            models.SuggestedTopic.content_plan_id == plan.id,
            models.SuggestedTopic.is_active == True
        ).group_by(
            models.SuggestedTopic.category,
            models.SuggestedTopic.status
        )
        
        topics_stats = topics_query.all()
        
        # Calculate totals
        total_topics = sum(stat.count for stat in topics_stats)
        approved_topics = sum(stat.count for stat in topics_stats if stat.status == 'approved')
        blog_topics = sum(stat.count for stat in topics_stats if stat.category == 'blog')
        sm_topics = sum(stat.count for stat in topics_stats if stat.category == 'social_media')
        
        # Get variant count
        variant_count = db.query(func.count(models.ContentVariant.id)).join(
            models.ContentDraft
        ).join(
            models.SuggestedTopic
        ).filter(
            models.SuggestedTopic.content_plan_id == plan.id,
            models.ContentVariant.is_active == True
        ).scalar() or 0
        
        # Get scheduled posts count
        scheduled_count = db.query(func.count(models.ScheduledPost.id)).filter(
            models.ScheduledPost.content_plan_id == plan.id
        ).scalar() or 0
        
        result.append({
            "id": plan.id,
            "plan_period": plan.plan_period,
            "status": plan.status,
            "blog_posts_quota": plan.blog_posts_quota,
            "sm_posts_quota": plan.sm_posts_quota,
            "created_at": plan.created_at.isoformat(),
            "updated_at": plan.updated_at.isoformat(),
            "content_stats": {
                "total_topics": total_topics,
                "approved_topics": approved_topics,
                "blog_topics": blog_topics,
                "sm_topics": sm_topics,
                "total_variants": variant_count,
                "scheduled_posts": scheduled_count
            }
        })
    
    return result


@router.get("/content-plans/{plan_id}/visualization")
async def get_content_plan_visualization(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed visualization data for a content plan
    
    Returns blog posts and social media posts with their content and relationships
    """
    
    # Get content plan
    plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    # Check access
    if not crud.organization_crud.user_has_access(db, plan.organization_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get all blog topics with their variants
    blog_topics = db.query(models.SuggestedTopic).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.SuggestedTopic.category == 'blog',
        models.SuggestedTopic.is_active == True
    ).all()
    
    blog_posts = []
    for topic in blog_topics:
        # Get draft and variants
        draft = db.query(models.ContentDraft).filter(
            models.ContentDraft.suggested_topic_id == topic.id,
            models.ContentDraft.is_active == True
        ).first()
        
        variants = []
        if draft:
            variants = db.query(models.ContentVariant).filter(
                models.ContentVariant.content_draft_id == draft.id,
                models.ContentVariant.is_active == True
            ).all()
        
        # Get scheduled date if exists
        scheduled_post = None
        if variants:
            scheduled_post = db.query(models.ScheduledPost).filter(
                models.ScheduledPost.content_variant_id.in_([v.id for v in variants])
            ).first()
        
        blog_posts.append({
            "id": topic.id,
            "type": "blog",
            "title": topic.title,
            "content": topic.description,
            "scheduled_date": scheduled_post.publication_date.isoformat() if scheduled_post else None,
            "variants": [
                {
                    "id": v.id,
                    "platform_name": v.platform_name,
                    "content_text": v.content_text
                } for v in variants
            ]
        })
    
    # Get all social media topics with their variants
    sm_topics = db.query(models.SuggestedTopic).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.SuggestedTopic.category == 'social_media',
        models.SuggestedTopic.is_active == True
    ).all()
    
    social_posts = []
    for topic in sm_topics:
        # Get draft and variants
        draft = db.query(models.ContentDraft).filter(
            models.ContentDraft.suggested_topic_id == topic.id,
            models.ContentDraft.is_active == True
        ).first()
        
        variants = []
        if draft:
            variants = db.query(models.ContentVariant).filter(
                models.ContentVariant.content_draft_id == draft.id,
                models.ContentVariant.is_active == True
            ).all()
        
        # Determine source type
        source_type = "standalone"
        if topic.parent_topic_id:
            source_type = "blog-correlated"
        elif topic.meta_data and topic.meta_data.get("source") == "brief":
            source_type = "brief-based"
        
        # For each variant (platform), create a separate entry
        if variants:
            for variant in variants:
                scheduled_post = db.query(models.ScheduledPost).filter(
                    models.ScheduledPost.content_variant_id == variant.id
                ).first()
                
                social_posts.append({
                    "id": topic.id,
                    "type": "social_media",
                    "title": topic.title,
                    "content": topic.description,
                    "platform": variant.platform_name,
                    "parent_id": topic.parent_topic_id,
                    "source_type": source_type,
                    "scheduled_date": scheduled_post.publication_date.isoformat() if scheduled_post else None,
                    "variants": [{
                        "id": variant.id,
                        "platform_name": variant.platform_name,
                        "content_text": variant.content_text
                    }]
                })
        else:
            # If no variants yet, still show the topic
            social_posts.append({
                "id": topic.id,
                "type": "social_media",
                "title": topic.title,
                "content": topic.description,
                "platform": None,
                "parent_id": topic.parent_topic_id,
                "source_type": source_type,
                "scheduled_date": None,
                "variants": []
            })
    
    return {
        "plan": {
            "id": plan.id,
            "plan_period": plan.plan_period,
            "status": plan.status
        },
        "blogPosts": blog_posts,
        "socialPosts": social_posts
    }