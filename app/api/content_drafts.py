"""
Content Drafts API endpoints.
Implements the complete API for content draft management with revision workflow.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud, schemas
from app.core.dependencies import get_current_active_user
from app.db.models import User, ScheduledPost

router = APIRouter()


@router.post("/scheduled-posts/{post_id}/generate-draft", status_code=http_status.HTTP_202_ACCEPTED)
async def generate_draft_for_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate initial draft for a scheduled post.
    
    This endpoint triggers the generate_draft_task in basic mode (no revision).
    
    - **post_id**: ID of the scheduled post
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    """
    
    # Get the scheduled post
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == post_id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    # Get content plan to check organization access
    content_plan = crud.content_plan_crud.get_by_id(db, scheduled_post.content_plan_id)
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
    
    try:
        # Import and trigger content draft generation task
        from app.tasks.content_draft import generate_draft_task
        
        result = generate_draft_task.delay(
            scheduled_post_id=post_id,
            revision_mode=None,  # Initial draft
            revision_context=None
        )
        
        return {
            "status": "ACCEPTED",
            "message": "Draft generation started successfully",
            "task_id": result.id,
            "post_id": post_id,
            "expected_completion_time": "2-5 minutes",
            "next_steps": [
                "1. Content analysis and strategy retrieval",
                "2. AI-powered content generation with Author-Reviewer loop",
                "3. Draft saved to database with status 'pending_approval'"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting draft generation: {str(e)}"
        )


@router.get("/content-plans/{plan_id}/drafts", response_model=List[schemas.ContentDraft])
async def get_drafts_for_content_plan(
    plan_id: int,
    status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all content drafts for a content plan.
    
    This endpoint retrieves all ContentDraft objects waiting for approval
    for the given content plan.
    
    - **plan_id**: ID of the content plan
    - **status**: Optional filter by draft status (pending_approval, approved, rejected)
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: List of ContentDraft objects
    """
    
    # Get the content plan
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
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
    
    # Get drafts for the content plan
    drafts = crud.content_draft_crud.get_drafts_by_content_plan_id(db, plan_id, status)
    
    # Add variants_count to each draft
    for draft in drafts:
        draft.variants_count = len(draft.variants) if draft.variants else 0
    
    return drafts


@router.patch("/content-drafts/{draft_id}/status", response_model=schemas.ContentDraft)
async def update_draft_status(
    draft_id: int,
    status_update: schemas.DraftStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of a content draft.
    
    This endpoint updates the status field of a ContentDraft to accept or reject it.
    
    - **draft_id**: ID of the content draft to update
    - **status_update**: DraftStatusUpdate object with the new status
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: Updated ContentDraft object
    """
    
    # Get the content draft
    content_draft = crud.content_draft_crud.get_by_id(db, draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    # Get scheduled post and content plan for authorization
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == content_draft.scheduled_post_id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    content_plan = crud.content_plan_crud.get_by_id(db, scheduled_post.content_plan_id)
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
    
    # Validate status value
    allowed_statuses = ['pending_approval', 'approved', 'rejected']
    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
        )
    
    # Update the draft status
    try:
        updated_draft = crud.content_draft_crud.update_status(db, draft_id, status_update.status)
        if not updated_draft:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update draft status"
            )
        
        return updated_draft
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating draft status: {str(e)}"
        )


@router.post("/content-drafts/{draft_id}/request-revision", status_code=http_status.HTTP_202_ACCEPTED)
async def request_draft_revision(
    draft_id: int,
    revision_request: schemas.DraftRevisionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Request revision of a content draft with feedback.
    
    This endpoint triggers generate_draft_task in 'feedback' mode to improve
    the draft based on operator feedback.
    
    - **draft_id**: ID of the content draft to revise
    - **revision_request**: DraftRevisionRequest with feedback text and context
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    """
    
    # Get the content draft
    content_draft = crud.content_draft_crud.get_by_id(db, draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    # Get scheduled post and content plan for authorization
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == content_draft.scheduled_post_id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    content_plan = crud.content_plan_crud.get_by_id(db, scheduled_post.content_plan_id)
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
    
    try:
        # Prepare revision context
        revision_context = {
            "feedback_text": revision_request.feedback_text,
            "previous_content": content_draft.content_text,
            "user_id": current_user.id,
            "additional_context": revision_request.revision_context or {}
        }
        
        # Import and trigger content draft revision task
        from app.tasks.content_draft import generate_draft_task
        
        result = generate_draft_task.delay(
            scheduled_post_id=content_draft.scheduled_post_id,
            revision_mode='feedback',
            revision_context=revision_context
        )
        
        return {
            "status": "ACCEPTED",
            "message": "Draft revision started successfully",
            "task_id": result.id,
            "draft_id": draft_id,
            "revision_mode": "feedback",
            "expected_completion_time": "2-5 minutes",
            "next_steps": [
                "1. Analysis of feedback and previous content",
                "2. AI-powered content revision with Author-Reviewer loop",
                "3. New draft version saved with status 'pending_approval'"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting draft revision: {str(e)}"
        )


@router.post("/content-drafts/{draft_id}/regenerate", status_code=http_status.HTTP_202_ACCEPTED)
async def regenerate_draft(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenerate a content draft from scratch after rejection.
    
    This endpoint triggers generate_draft_task in 'regenerate' mode to create
    a completely new version avoiding issues from the rejected draft.
    
    - **draft_id**: ID of the rejected content draft
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    """
    
    # Get the content draft
    content_draft = crud.content_draft_crud.get_by_id(db, draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    # Check if draft is in rejected status
    if content_draft.status != 'rejected':
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Draft must be in 'rejected' status to regenerate"
        )
    
    # Get scheduled post and content plan for authorization
    scheduled_post = db.query(ScheduledPost).filter(
        ScheduledPost.id == content_draft.scheduled_post_id
    ).first()
    
    if not scheduled_post:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Scheduled post not found"
        )
    
    content_plan = crud.content_plan_crud.get_by_id(db, scheduled_post.content_plan_id)
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
    
    try:
        # Get latest revision to understand rejection reason
        latest_revision = crud.draft_revision_crud.get_latest_by_draft_id(db, draft_id)
        rejection_reason = latest_revision.feedback_text if latest_revision else "Content did not meet quality standards"
        
        # Prepare regeneration context
        revision_context = {
            "previous_content": content_draft.content_text,
            "rejection_reason": rejection_reason,
            "user_id": current_user.id,
            "additional_context": {
                "original_draft_id": draft_id,
                "original_version": content_draft.version
            }
        }
        
        # Import and trigger content draft regeneration task
        from app.tasks.content_draft import generate_draft_task
        
        result = generate_draft_task.delay(
            scheduled_post_id=content_draft.scheduled_post_id,
            revision_mode='regenerate',
            revision_context=revision_context
        )
        
        return {
            "status": "ACCEPTED",
            "message": "Draft regeneration started successfully",
            "task_id": result.id,
            "draft_id": draft_id,
            "revision_mode": "regenerate",
            "expected_completion_time": "2-5 minutes",
            "next_steps": [
                "1. Analysis of rejected content and failure reasons",
                "2. AI-powered content regeneration with new approach",
                "3. New draft version saved with status 'pending_approval'"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting draft regeneration: {str(e)}"
        )


@router.get("/content-drafts/{draft_id}", response_model=schemas.ContentDraft)
async def get_draft_details(
    draft_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get detailed information about a content draft including revision history.
    
    - **draft_id**: ID of the content draft
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: ContentDraft object with revisions
    """
    
    # Get the content draft
    content_draft = crud.content_draft_crud.get_by_id(db, draft_id)
    if not content_draft:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Content draft not found"
        )
    
    # Get suggested topic to find the organization through content plan
    if not content_draft.suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Get content plan through suggested topic
    content_plan = crud.content_plan_crud.get_by_id(db, content_draft.suggested_topic.content_plan_id)
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
    
    # ContentDraft already has revisions loaded via eager loading in CRUD
    return content_draft