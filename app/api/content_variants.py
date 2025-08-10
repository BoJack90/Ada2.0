"""
Content Variants API endpoints.
Implements the complete API for content variant management with revision workflow.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud, schemas
from app.core.dependencies import get_current_active_user
from app.db.models import User, ContentDraft, ContentVariant


def get_organization_from_content_draft(db: Session, content_draft_id: int):
    """Helper function to get organization_id from content_draft"""
    content_draft = crud.content_draft_crud.get_by_id(db, content_draft_id)
    if not content_draft:
        return None
    
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        return None
        
    content_plan = crud.content_plan_crud.get_by_id(db, suggested_topic.content_plan_id)
    if not content_plan:
        return None
        
    return content_plan.organization_id


router = APIRouter()


@router.get("/content-drafts/{draft_id}/variants", response_model=List[schemas.ContentVariant])
async def get_variants_for_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all variants for a specific content draft.
    
    This endpoint retrieves all ContentVariant objects for a given ContentDraft.
    
    - **draft_id**: ID of the content draft
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: List of ContentVariant objects
    """
    
    # Get the content draft
    content_draft = crud.content_draft_crud.get_by_id(db, draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    # Get suggested topic to check organization access
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Get content plan to check organization access
    content_plan = crud.content_plan_crud.get_by_id(db, suggested_topic.content_plan_id)
    if not content_plan:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content plan not found"
        )
    
    # Check if user has access to the organization
    if not crud.organization_crud.user_has_access(db, content_plan.organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Get variants for the content draft
    variants = crud.content_variant_crud.get_by_content_draft_id(db, draft_id)
    return variants


@router.patch("/content-variants/{variant_id}", response_model=schemas.ContentVariant)
async def update_variant_content(
    variant_id: int,
    content_update: schemas.VariantContentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the content text of a specific variant.
    
    This endpoint updates the content_text field of a ContentVariant.
    
    - **variant_id**: ID of the content variant to update
    - **content_update**: VariantContentUpdate object with new content text
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: Updated ContentVariant object
    """
    
    # Get the content variant
    content_variant = crud.content_variant_crud.get_by_id(db, variant_id)
    if not content_variant:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content variant not found"
        )
    
    # Get content draft and suggested topic for authorization
    content_draft = crud.content_draft_crud.get_by_id(db, content_variant.content_draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Check if user has access to the organization
    organization_id = get_organization_from_content_draft(db, content_draft.id)
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Update the variant content
    try:
        updated_variant = crud.content_variant_crud.update_content(
            db, variant_id, content_update.content_text
        )
        if not updated_variant:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update variant content"
            )
        
        return updated_variant
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating variant content: {str(e)}"
        )


@router.patch("/content-variants/{variant_id}/status", response_model=schemas.ContentVariant)
async def update_variant_status(
    variant_id: int,
    status_update: schemas.VariantStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of a content variant.
    
    This endpoint updates the status field of a ContentVariant to approve or reject it.
    
    - **variant_id**: ID of the content variant to update
    - **status_update**: VariantStatusUpdate object with the new status
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: Updated ContentVariant object
    """
    
    # Get the content variant
    content_variant = crud.content_variant_crud.get_by_id(db, variant_id)
    if not content_variant:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content variant not found"
        )
    
    # Get content draft and suggested topic for authorization
    content_draft = crud.content_draft_crud.get_by_id(db, content_variant.content_draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Check if user has access to the organization
    organization_id = get_organization_from_content_draft(db, content_draft.id)
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Validate status value
    allowed_statuses = ['pending_approval', 'approved', 'rejected', 'needs_revision']
    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
        )
    
    # Update the variant status
    try:
        updated_variant = crud.content_variant_crud.update_status(
            db, variant_id, status_update.status
        )
        if not updated_variant:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update variant status"
            )
        
        return updated_variant
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating variant status: {str(e)}"
        )


@router.post("/content-variants/{variant_id}/request-revision", status_code=http_status.HTTP_202_ACCEPTED)
async def request_variant_revision(
    variant_id: int,
    revision_request: schemas.VariantRevisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Request revision of a content variant with feedback.
    
    This endpoint triggers generate_draft_task in 'feedback' mode to improve
    the variant based on operator feedback.
    
    - **variant_id**: ID of the content variant to revise
    - **revision_request**: VariantRevisionRequest with feedback text
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    """
    
    # Get the content variant
    content_variant = crud.content_variant_crud.get_by_id(db, variant_id)
    if not content_variant:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content variant not found"
        )
    
    # Get content draft and suggested topic for authorization
    content_draft = crud.content_draft_crud.get_by_id(db, content_variant.content_draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Check if user has access to the organization
    organization_id = get_organization_from_content_draft(db, content_draft.id)
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    try:
        # Import generate_draft_task for variant revision
        from app.tasks.variant_generation import generate_single_variant_task
        
        # Prepare revision context
        revision_context = {
            "feedback": revision_request.feedback,
            "previous_content": content_variant.content_text,
            "platform_name": content_variant.platform_name,
            "user_id": current_user.id,
            "variant_id": variant_id
        }
        
        # Trigger variant revision task
        result = generate_single_variant_task.delay(
            suggested_topic_id=content_draft.suggested_topic_id,
            platform_name=content_variant.platform_name,
            revision_mode='feedback',
            revision_context=revision_context
        )
        
        return {
            "status": "ACCEPTED",
            "message": "Variant revision started successfully",
            "task_id": result.id,
            "variant_id": variant_id,
            "platform_name": content_variant.platform_name,
            "expected_completion_time": "2-5 minutes",
            "next_steps": [
                "1. AI analysis of feedback and current content",
                "2. Generation of improved variant",
                "3. New variant created with 'pending_approval' status"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting variant revision: {str(e)}"
        )


@router.post("/content-variants/{variant_id}/regenerate", status_code=http_status.HTTP_202_ACCEPTED)
async def regenerate_variant(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenerate a content variant without specific feedback.
    
    This endpoint triggers generate_draft_task in 'regenerate' mode to create
    a new version of the variant.
    
    - **variant_id**: ID of the content variant to regenerate
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    """
    
    # Get the content variant
    content_variant = crud.content_variant_crud.get_by_id(db, variant_id)
    if not content_variant:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content variant not found"
        )
    
    # Get content draft and suggested topic for authorization
    content_draft = crud.content_draft_crud.get_by_id(db, content_variant.content_draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Check if user has access to the organization
    organization_id = get_organization_from_content_draft(db, content_draft.id)
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    try:
        # Import generate_single_variant_task for variant regeneration
        from app.tasks.variant_generation import generate_single_variant_task
        
        # Prepare revision context
        revision_context = {
            "previous_content": content_variant.content_text,
            "platform_name": content_variant.platform_name,
            "user_id": current_user.id,
            "variant_id": variant_id
        }
        
        # Trigger variant regeneration task
        result = generate_single_variant_task.delay(
            suggested_topic_id=content_draft.suggested_topic_id,
            platform_name=content_variant.platform_name,
            revision_mode='regenerate',
            revision_context=revision_context
        )
        
        return {
            "status": "ACCEPTED",
            "message": "Variant regeneration started successfully",
            "task_id": result.id,
            "variant_id": variant_id,
            "platform_name": content_variant.platform_name,
            "expected_completion_time": "2-5 minutes",
            "next_steps": [
                "1. AI analysis of current content and strategy",
                "2. Generation of new variant version",
                "3. New variant created with 'pending_approval' status"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting variant regeneration: {str(e)}"
        )


@router.get("/content-variants/{variant_id}", response_model=schemas.ContentVariant)
async def get_variant_details(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of a specific content variant.
    
    This endpoint retrieves detailed information about a ContentVariant.
    
    - **variant_id**: ID of the content variant
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: ContentVariant object with details
    """
    
    # Get the content variant
    content_variant = crud.content_variant_crud.get_by_id(db, variant_id)
    if not content_variant:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content variant not found"
        )
    
    # Get content draft and suggested topic for authorization
    content_draft = crud.content_draft_crud.get_by_id(db, content_variant.content_draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, content_draft.suggested_topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Check if user has access to the organization
    organization_id = get_organization_from_content_draft(db, content_draft.id)
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    return content_variant 