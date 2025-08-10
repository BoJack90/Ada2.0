"""
Content visualization API endpoints for full content display
"""

from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session, joinedload
from typing import List, Dict, Any
from app.db.database import get_db
from app.db import crud, models
from app.core.dependencies import get_current_active_user
from app.db.models import User

router = APIRouter()


@router.get("/content-plans/{plan_id}/full-content")
async def get_plan_full_content(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Get full content for visualization including complete text for all drafts and variants.
    Groups content by blog posts and their related social media posts.
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
    
    # Get all drafts with full relationships - only for approved topics
    drafts = db.query(models.ContentDraft).join(
        models.SuggestedTopic
    ).options(
        joinedload(models.ContentDraft.suggested_topic).joinedload(models.SuggestedTopic.parent),
        joinedload(models.ContentDraft.suggested_topic).joinedload(models.SuggestedTopic.content_plan),
        joinedload(models.ContentDraft.variants)
    ).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.SuggestedTopic.status == "approved",  # Only show content for approved topics
        models.ContentDraft.is_active == True
    ).all()
    
    # Organize content
    blog_posts = []
    social_posts_by_parent = {}
    standalone_social_posts = []
    
    for draft in drafts:
        topic = draft.suggested_topic
        
        # Prepare full variant data
        variants_data = []
        for variant in draft.variants:
            variants_data.append({
                "id": variant.id,
                "platform_name": variant.platform_name,
                "status": variant.status,
                "content_text": variant.content_text,  # Full text
                "created_at": variant.created_at.isoformat() if variant.created_at else None,
                "updated_at": variant.updated_at.isoformat() if variant.updated_at else None
            })
        
        draft_data = {
            "id": draft.id,
            "topic": {
                "id": topic.id,
                "title": topic.title,
                "description": topic.description,
                "category": topic.category
            },
            "status": draft.status,
            "variants": variants_data,
            "created_at": draft.created_at.isoformat() if draft.created_at else None,
            "updated_at": draft.updated_at.isoformat() if draft.updated_at else None
        }
        
        if topic.category == "blog":
            # Blog post
            blog_posts.append(draft_data)
        elif topic.category == "social_media":
            # Social media post
            if topic.parent_topic_id:
                # Correlated with blog post
                parent_title = topic.parent.title if topic.parent else f"parent_{topic.parent_topic_id}"
                if parent_title not in social_posts_by_parent:
                    social_posts_by_parent[parent_title] = []
                social_posts_by_parent[parent_title].append(draft_data)
            else:
                # Standalone social post
                standalone_social_posts.append(draft_data)
    
    # Sort blog posts by creation date
    blog_posts.sort(key=lambda x: x["created_at"], reverse=True)
    
    # Create final structure with blog posts and their related social posts
    organized_content = []
    for blog_post in blog_posts:
        blog_title = blog_post["topic"]["title"]
        related_social = social_posts_by_parent.get(blog_title, [])
        
        organized_content.append({
            "blog_post": blog_post,
            "related_social_posts": related_social
        })
    
    return {
        "plan": {
            "id": content_plan.id,
            "plan_period": content_plan.plan_period,
            "status": content_plan.status,
            "blog_posts_quota": content_plan.blog_posts_quota,
            "sm_posts_quota": content_plan.sm_posts_quota
        },
        "organized_content": organized_content,
        "standalone_social_posts": standalone_social_posts,
        "statistics": {
            "total_blog_posts": len(blog_posts),
            "total_social_posts": len(social_posts_by_parent) + len(standalone_social_posts),
            "correlated_social_posts": sum(len(posts) for posts in social_posts_by_parent.values()),
            "standalone_social_posts": len(standalone_social_posts)
        }
    }