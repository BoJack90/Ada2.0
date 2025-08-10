"""
Test content plans API
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app.db.database import get_db
from app.db import models

router = APIRouter()


@router.get("/api/test/content-plans")
async def test_content_plans(
    organization_id: int,
    db: Session = Depends(get_db)
):
    """
    Simple test endpoint without auth
    """
    
    # Get plans
    plans = db.query(models.ContentPlan).filter(
        models.ContentPlan.organization_id == organization_id
    ).all()
    
    result = []
    for plan in plans:
        # Count topics
        topic_count = db.query(func.count(models.SuggestedTopic.id)).filter(
            models.SuggestedTopic.content_plan_id == plan.id
        ).scalar() or 0
        
        result.append({
            "id": plan.id,
            "plan_period": plan.plan_period,
            "status": plan.status,
            "blog_posts_quota": plan.blog_posts_quota,
            "sm_posts_quota": plan.sm_posts_quota,
            "topic_count": topic_count
        })
    
    return {
        "organization_id": organization_id,
        "plans": result,
        "count": len(result)
    }