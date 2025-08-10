"""
API endpoints for controlling content generation
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.core.dependencies import get_db, get_current_user
from app.db.models import User, ContentPlan, SuggestedTopic
from app.db import crud
from app.tasks.selective_generation import (
    generate_variants_for_approved_sm_topics,
    generate_single_topic_variants
)

router = APIRouter()


class GenerateVariantsRequest(BaseModel):
    topic_ids: Optional[List[int]] = None
    platform_names: Optional[List[str]] = None
    generate_all_approved: bool = False


class BulkTopicApprovalRequest(BaseModel):
    topic_ids: List[int]
    status: str  # "approved", "rejected", "suggested"
    generate_variants: bool = False


@router.post("/content-plans/{plan_id}/generate-sm-variants")
async def generate_sm_variants(
    plan_id: int,
    request: GenerateVariantsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Generate content variants for SM topics
    
    Options:
    - Generate for specific topic IDs
    - Generate for all approved SM topics
    - Filter by platform names
    """
    
    # Validate access
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Validate request
    if not request.topic_ids and not request.generate_all_approved:
        raise HTTPException(
            status_code=400, 
            detail="Either topic_ids or generate_all_approved must be specified"
        )
    
    if request.generate_all_approved:
        # Generate for all approved SM topics
        task = generate_variants_for_approved_sm_topics.delay(plan_id)
        
        return {
            "message": "Generation started for all approved SM topics",
            "task_id": task.id,
            "status": "PENDING"
        }
    
    elif request.topic_ids:
        # Validate topics belong to the plan and are SM topics
        topics = db.query(SuggestedTopic).filter(
            SuggestedTopic.id.in_(request.topic_ids),
            SuggestedTopic.content_plan_id == plan_id,
            SuggestedTopic.category == "social_media",
            SuggestedTopic.is_active == True
        ).all()
        
        if len(topics) != len(request.topic_ids):
            raise HTTPException(
                status_code=400,
                detail="Some topic IDs are invalid or not SM topics"
            )
        
        # Generate variants for each topic
        task_ids = []
        for topic_id in request.topic_ids:
            task = generate_single_topic_variants.delay(
                topic_id, 
                request.platform_names
            )
            task_ids.append(task.id)
        
        return {
            "message": f"Generation started for {len(task_ids)} topics",
            "task_ids": task_ids,
            "status": "PENDING"
        }


@router.post("/content-plans/{plan_id}/topics/bulk-approval")
async def bulk_approve_topics(
    plan_id: int,
    request: BulkTopicApprovalRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Bulk approve/reject topics with optional variant generation
    """
    
    # Validate access
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Validate status
    if request.status not in ["approved", "rejected", "suggested"]:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    # Update topics
    updated_count = db.query(SuggestedTopic).filter(
        SuggestedTopic.id.in_(request.topic_ids),
        SuggestedTopic.content_plan_id == plan_id,
        SuggestedTopic.is_active == True
    ).update({
        "status": request.status,
        "updated_at": datetime.utcnow()
    })
    
    db.commit()
    
    response = {
        "message": f"Updated {updated_count} topics to {request.status}",
        "updated_count": updated_count
    }
    
    # Generate variants if requested and topics were approved
    if request.generate_variants and request.status == "approved":
        # Filter for SM topics only
        sm_topic_ids = db.query(SuggestedTopic.id).filter(
            SuggestedTopic.id.in_(request.topic_ids),
            SuggestedTopic.category == "social_media",
            SuggestedTopic.status == "approved",
            SuggestedTopic.is_active == True
        ).all()
        
        sm_topic_ids = [t[0] for t in sm_topic_ids]
        
        if sm_topic_ids:
            task_ids = []
            for topic_id in sm_topic_ids:
                task = generate_single_topic_variants.delay(topic_id)
                task_ids.append(task.id)
            
            response["variant_generation"] = {
                "started": True,
                "topic_count": len(sm_topic_ids),
                "task_ids": task_ids
            }
    
    return response


@router.get("/content-plans/{plan_id}/generation-status")
async def get_generation_status(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Dict[str, Any]:
    """
    Get content generation status for a plan
    """
    
    # Validate access
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Get topic counts by status and category
    topic_stats = db.query(
        SuggestedTopic.category,
        SuggestedTopic.status,
        func.count(SuggestedTopic.id).label('count')
    ).filter(
        SuggestedTopic.content_plan_id == plan_id,
        SuggestedTopic.is_active == True
    ).group_by(
        SuggestedTopic.category,
        SuggestedTopic.status
    ).all()
    
    # Get variant counts
    from sqlalchemy import func
    variant_count = db.query(func.count(ContentVariant.id)).join(
        ContentDraft
    ).join(
        SuggestedTopic
    ).filter(
        SuggestedTopic.content_plan_id == plan_id,
        ContentVariant.is_active == True
    ).scalar()
    
    # Format statistics
    stats = {
        "topics": {},
        "variants": {
            "total": variant_count
        }
    }
    
    for category, status, count in topic_stats:
        if category not in stats["topics"]:
            stats["topics"][category] = {}
        stats["topics"][category][status] = count
    
    return stats