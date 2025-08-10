"""
API endpoints for content briefs and correlation rules
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import base64
import os
from datetime import datetime

from app.core.dependencies import get_db, get_current_user
from app.db.models import User
from app.db.crud_content_brief import content_brief_crud, correlation_rule_crud
from app.db.schemas_content_brief import (
    ContentBrief, ContentBriefCreate, ContentBriefUpdate,
    CorrelationRule, CorrelationRuleCreate, CorrelationRuleUpdate,
    PlatformDistribution
)
from app.tasks.brief_analysis import analyze_brief_task

router = APIRouter()


@router.post("/content-plans/{plan_id}/briefs", response_model=ContentBrief)
async def create_content_brief(
    plan_id: int,
    title: str = Form(...),
    description: Optional[str] = Form(None),
    priority_level: int = Form(5),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new content brief with optional file upload"""
    
    # Validate content plan exists and user has access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    # Check user has access to organization
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Create brief object
    brief_create = ContentBriefCreate(
        content_plan_id=plan_id,
        title=title,
        description=description,
        priority_level=priority_level
    )
    
    # Process file if uploaded
    if file:
        # Validate file type
        allowed_types = ["application/pdf", "application/msword", 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                        "text/plain", "text/html", "application/rtf"]
        
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported")
        
        # Read file content
        file_content = await file.read()
        file_content_b64 = base64.b64encode(file_content).decode('utf-8')
        
        brief_create.file_type = file.content_type
        brief_create.file_content = file_content_b64
    
    # Create brief in database
    brief = content_brief_crud.create(db, brief_create)
    
    # If file was uploaded, trigger AI analysis
    if file:
        # Save file to storage
        file_dir = f"/app/uploads/briefs/{plan_id}"
        os.makedirs(file_dir, exist_ok=True)
        file_path = f"{file_dir}/{brief.id}_{file.filename}"
        
        with open(file_path, "wb") as f:
            f.write(file_content)
        
        # Update brief with file path
        brief.file_path = file_path
        db.commit()
        
        # Trigger async analysis
        analyze_brief_task.delay(
            brief_id=brief.id,
            file_content_b64=file_content_b64,
            file_mime_type=file.content_type
        )
    
    return brief


@router.get("/content-plans/{plan_id}/briefs", response_model=List[ContentBrief])
def get_content_briefs(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get all briefs for a content plan"""
    
    # Validate access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    return content_brief_crud.get_by_content_plan(db, plan_id)


@router.get("/briefs/{brief_id}", response_model=ContentBrief)
def get_content_brief(
    brief_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get a specific content brief"""
    
    brief = content_brief_crud.get_by_id(db, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    # Check access through content plan
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, brief.content_plan_id)
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    return brief


@router.put("/briefs/{brief_id}", response_model=ContentBrief)
def update_content_brief(
    brief_id: int,
    brief_update: ContentBriefUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a content brief"""
    
    brief = content_brief_crud.get_by_id(db, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    # Check access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, brief.content_plan_id)
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    return content_brief_crud.update(db, brief_id, brief_update)


@router.delete("/briefs/{brief_id}")
def delete_content_brief(
    brief_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a content brief"""
    
    brief = content_brief_crud.get_by_id(db, brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    
    # Check access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, brief.content_plan_id)
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Delete file if exists
    if brief.file_path and os.path.exists(brief.file_path):
        os.remove(brief.file_path)
    
    content_brief_crud.delete(db, brief_id)
    return {"detail": "Brief deleted successfully"}


# Correlation Rules Endpoints

@router.post("/content-plans/{plan_id}/correlation-rules", response_model=CorrelationRule)
def create_correlation_rules(
    plan_id: int,
    rules: CorrelationRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create or update correlation rules for a content plan"""
    
    # Validate access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check if rules already exist
    existing_rules = correlation_rule_crud.get_by_content_plan(db, plan_id)
    if existing_rules:
        # Update existing rules
        return correlation_rule_crud.update(db, plan_id, CorrelationRuleUpdate(**rules.dict()))
    
    # Create new rules
    rules.content_plan_id = plan_id
    return correlation_rule_crud.create(db, rules)


@router.get("/content-plans/{plan_id}/correlation-rules", response_model=Optional[CorrelationRule])
def get_correlation_rules(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get correlation rules for a content plan"""
    
    # Validate access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    return correlation_rule_crud.get_by_content_plan(db, plan_id)


@router.get("/content-plans/{plan_id}/sm-distribution")
def calculate_sm_distribution(
    plan_id: int,
    blog_posts_count: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Calculate SM posts distribution based on correlation rules"""
    
    # Validate access
    from app.db.crud import content_plan_crud
    content_plan = content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    if not any(org.id == content_plan.organization_id for org in current_user.organizations):
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Calculate distribution
    distribution = correlation_rule_crud.calculate_total_sm_posts(db, plan_id, blog_posts_count)
    
    # Get platform-specific distribution if rules exist
    rules = correlation_rule_crud.get_by_content_plan(db, plan_id)
    platform_distribution = []
    
    if rules and rules.platform_rules:
        for platform, count in rules.platform_rules.items():
            platform_distribution.append(PlatformDistribution(
                platform=platform,
                posts_count=count,
                correlation_type="mixed"
            ))
    
    return {
        "total_distribution": distribution,
        "platform_distribution": platform_distribution
    }