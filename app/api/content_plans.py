from fastapi import APIRouter, Depends, HTTPException, status as http_status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from celery import chain
from datetime import datetime
import logging
import os
import uuid
import base64
import json

from app.db.database import get_db
from app.db import schemas, crud
from app.db.schemas_content_brief import ContentBriefCreate
from app.db.crud_content_brief import content_brief_crud
from app.core.dependencies import get_current_active_user
from app.db.models import User

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/content-plans", response_model=schemas.ContentPlan, status_code=http_status.HTTP_201_CREATED)
async def create_content_plan(
    organization_id: int = Form(...),
    plan_period: str = Form(...),
    blog_posts_quota: int = Form(...),
    sm_posts_quota: int = Form(...),
    correlate_posts: bool = Form(True),
    scheduling_mode: str = Form("auto"),
    scheduling_preferences: Optional[str] = Form(None),
    meta_data: Optional[str] = Form(None),
    brief_file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new content plan.
    
    - **organization_id**: ID of the organization
    - **plan_period**: Period for the content plan
    - **blog_posts_quota**: Number of blog posts
    - **sm_posts_quota**: Number of social media posts
    - **correlate_posts**: Whether to correlate posts
    - **scheduling_mode**: Scheduling mode (auto, with_guidelines, visual)
    - **scheduling_preferences**: Optional scheduling preferences as JSON string
    - **meta_data**: Optional metadata as JSON string
    - **brief_file**: Optional uploaded file (PDF, DOC, DOCX, TXT, RTF)
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    """
    
    # Log all received form fields for debugging
    logger.info(f"Creating content plan with form data: organization_id={organization_id}, plan_period={plan_period}, "
                f"blog_posts_quota={blog_posts_quota}, sm_posts_quota={sm_posts_quota}, correlate_posts={correlate_posts}, "
                f"scheduling_mode={scheduling_mode}, scheduling_preferences={scheduling_preferences}, meta_data={meta_data}, "
                f"brief_file={brief_file.filename if brief_file else 'None'}")
    
    # Check if user has access to the organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Verify that the organization exists
    organization = crud.organization_crud.get_by_id(db, organization_id)
    if not organization:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    # Handle file upload if provided
    file_path = None
    if brief_file:
        # Validate file type
        allowed_types = ['.pdf', '.doc', '.docx', '.txt', '.rtf']
        file_extension = os.path.splitext(brief_file.filename)[1].lower()
        
        if file_extension not in allowed_types:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_extension} not allowed. Supported types: {', '.join(allowed_types)}"
            )
        
        # Create uploads directory if it doesn't exist
        upload_dir = "/app/uploads/briefs"
        os.makedirs(upload_dir, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(upload_dir, unique_filename)
        
        # Save file
        try:
            content = await brief_file.read()
            with open(file_path, 'wb') as f:
                f.write(content)
        except Exception as e:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error saving file: {str(e)}"
            )
    
    # Create the content plan
    try:
        # Parse meta_data if provided
        parsed_meta_data = None
        if meta_data:
            try:
                logger.info(f"Received meta_data string: {meta_data}")
                parsed_meta_data = json.loads(meta_data)
                logger.info(f"Successfully parsed meta_data: {parsed_meta_data}")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse meta_data JSON: {meta_data}, error: {str(e)}")
                # Set default meta_data if parsing fails
                parsed_meta_data = {
                    'generation_method': 'standard',
                    'use_deep_research': False,
                    'research_depth': 'deep'
                }
        else:
            logger.warning("No meta_data received in request - setting defaults")
            # Set default meta_data if not provided
            parsed_meta_data = {
                'generation_method': 'standard',
                'use_deep_research': False,
                'research_depth': 'deep'
            }
        
        # Create ContentPlanCreate object from form data
        plan_data = schemas.ContentPlanCreate(
            organization_id=organization_id,
            plan_period=plan_period,
            blog_posts_quota=blog_posts_quota,
            sm_posts_quota=sm_posts_quota,
            correlate_posts=correlate_posts,
            scheduling_mode=scheduling_mode,
            scheduling_preferences=scheduling_preferences,
            meta_data=parsed_meta_data
        )
        
        # Create content plan with brief file path if provided
        if file_path:
            logger.info(f"Brief file saved to: {file_path}")
            plan_data.brief_file_path = file_path
        
        db_content_plan = crud.content_plan_crud.create(db, plan_data)
        
        # Create ContentBrief record and trigger analysis if file was uploaded
        if file_path and brief_file:
            from app.tasks.brief_analysis import analyze_brief_task
            
            # Create brief record
            brief_data = ContentBriefCreate(
                content_plan_id=db_content_plan.id,
                title=f"Brief - {plan_data.plan_period}",
                description=f"Monthly brief for {plan_data.plan_period}",
                file_type=file_extension.replace('.', ''),
                priority_level=9  # High priority (scale 1-10)
            )
            
            db_brief = content_brief_crud.create(db, brief_data)
            
            # Update with file path
            db_brief.file_path = file_path
            db.commit()
            
            # Read file content for analysis
            with open(file_path, 'rb') as f:
                file_content_b64 = base64.b64encode(f.read()).decode('utf-8')
            
            # Trigger async analysis
            analyze_brief_task.delay(
                brief_id=db_brief.id,
                file_content_b64=file_content_b64,
                file_mime_type=brief_file.content_type
            )
            
            logger.info(f"Created ContentBrief {db_brief.id} and triggered analysis")
        return db_content_plan
    except Exception as e:
        # Clean up uploaded file if content plan creation fails
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating content plan: {str(e)}"
        )


@router.get("/content-plans", response_model=List[schemas.ContentPlan])
async def get_content_plans(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all content plans for an organization.
    
    - **organization_id**: ID of the organization
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    """
    
    # Check if user has access to the organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Get content plans for the organization
    content_plans = crud.content_plan_crud.get_organization_content_plans(db, organization_id)
    return content_plans


@router.get("/content-plans/{content_plan_id}", response_model=schemas.ContentPlan)
async def get_content_plan(
    content_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific content plan by ID.
    
    - **content_plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    """
    
    # Get the content plan
    content_plan = crud.content_plan_crud.get_by_id(db, content_plan_id)
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
    
    return content_plan


@router.put("/content-plans/{content_plan_id}", response_model=schemas.ContentPlan)
async def update_content_plan(
    content_plan_id: int,
    content_plan_update: schemas.ContentPlanUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a content plan.
    
    - **content_plan_id**: ID of the content plan to update
    - **content_plan_update**: ContentPlanUpdate object with fields to update
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    """
    
    # Get the content plan
    content_plan = crud.content_plan_crud.get_by_id(db, content_plan_id)
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
    
    # Update the content plan
    try:
        updated_content_plan = crud.content_plan_crud.update(db, content_plan_id, content_plan_update)
        return updated_content_plan
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating content plan: {str(e)}"
        )


@router.delete("/content-plans/{content_plan_id}", status_code=http_status.HTTP_204_NO_CONTENT)
async def delete_content_plan(
    content_plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a content plan (soft delete - marks as inactive).
    
    - **content_plan_id**: ID of the content plan to delete
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    """
    
    # Get the content plan
    content_plan = crud.content_plan_crud.get_by_id(db, content_plan_id)
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
    
    # Delete the content plan
    success = crud.content_plan_crud.delete(db, content_plan_id)
    if not success:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting content plan"
        )


@router.get("/content-plans/status/{status_name}", response_model=List[schemas.ContentPlan])
async def get_content_plans_by_status(
    status_name: str,
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all content plans by status for an organization.
    
    - **status_name**: Status of the content plans (new, generating_topics, pending_approval, complete)
    - **organization_id**: ID of the organization
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    """
    
    # Check if user has access to the organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Get content plans by status
    content_plans = crud.content_plan_crud.get_by_status(db, organization_id, status_name)
    return content_plans


@router.post("/content-plans/{plan_id}/generate", status_code=http_status.HTTP_202_ACCEPTED)
async def generate_content_plan_topics(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Start the content generation process for a content plan.
    
    This endpoint triggers the Celery task chain for generating blog topics:
    1. Contextualize task - gathers communication strategy and context
    2. Generate topics task - uses AI to generate blog topics
    
    - **plan_id**: ID of the content plan to process
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID for monitoring
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
    
    # Validate plan status
    if content_plan.status != 'new':
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Content plan must be in 'new' status to generate topics. Current status: {content_plan.status}"
        )
    
    # Check if correlate_posts is enabled
    if not content_plan.correlate_posts:
        raise HTTPException(
            status_code=http_status.HTTP_501_NOT_IMPLEMENTED,
            detail="Content generation without correlation is not implemented yet. Please enable correlate_posts."
        )
    
    try:
        # Update plan status to generating_topics
        content_plan.status = 'generating_topics'
        content_plan.updated_at = datetime.utcnow()
        db.commit()
        
        # Import Celery tasks
        from app.tasks.main_flow import contextualize_task, generate_and_save_blog_topics_task
        
        # Build and execute the task chain
        # Task 1: contextualize_task(plan_id) -> Task 2: generate_and_save_blog_topics_task(context_data, plan_id)
        task_chain = chain(
            contextualize_task.s(plan_id),
            generate_and_save_blog_topics_task.s(plan_id)
        )
        
        # Execute the chain
        result = task_chain.apply_async()
        
        return {
            "status": "ACCEPTED",
            "message": "Content generation started successfully",
            "task_id": result.id,
            "plan_id": plan_id,
            "current_status": "generating_topics",
            "expected_completion_time": "5-10 minutes",
            "next_steps": [
                "1. Context analysis and strategy retrieval",
                "2. AI-powered blog topics generation",
                "3. Topics saved to database",
                "4. Plan status updated to 'pending_blog_topic_approval'"
            ]
        }
        
    except Exception as e:
        # Rollback plan status on error
        try:
            content_plan.status = 'new'
            content_plan.updated_at = datetime.utcnow()
            db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting content generation: {str(e)}"
        )


@router.get("/content-plans/{plan_id}/suggested-topics", response_model=List[schemas.SuggestedTopic])
async def get_suggested_topics(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get all suggested topics for a content plan.
    
    This endpoint retrieves all SuggestedTopic objects related to the given plan_id
    directly through content_plan_id with all statuses (suggested, approved, rejected).
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: List of SuggestedTopic objects with all statuses
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
    
    # Get all suggested topics for this specific content plan
    suggested_topics = crud.suggested_topic_crud.get_by_content_plan_id(db, plan_id)
    return suggested_topics


@router.patch("/suggested-topics/{topic_id}/status", response_model=schemas.SuggestedTopic)
async def update_topic_status(
    topic_id: int,
    status_update: schemas.TopicStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update the status of a suggested topic.
    
    This endpoint updates the status field of a SuggestedTopic to a new value
    (e.g., 'approved' or 'rejected').
    
    - **topic_id**: ID of the suggested topic to update
    - **status_update**: TopicStatusUpdate object with the new status
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: Updated SuggestedTopic object
    """
    
    # Get the suggested topic
    suggested_topic = crud.suggested_topic_crud.get_by_id(db, topic_id)
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Check if user has access to the organization
    if not crud.organization_crud.user_has_access(db, suggested_topic.content_plan.organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Validate status value
    allowed_statuses = ['suggested', 'approved', 'rejected']
    if status_update.status not in allowed_statuses:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Allowed values: {', '.join(allowed_statuses)}"
        )
    
    # Update the topic status
    try:
        updated_topic = crud.suggested_topic_crud.update_status(db, topic_id, status_update.status)
        if not updated_topic:
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update topic status"
            )
        
        return updated_topic
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating topic status: {str(e)}"
        )


@router.post("/content-plans/{plan_id}/trigger-sm-generation", status_code=http_status.HTTP_202_ACCEPTED)
async def trigger_sm_generation(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Trigger the next stage of content generation process - Social Media topics and scheduling.
    
    This endpoint validates the ContentPlan status and approved topics count, then triggers
    the next Celery task chain for generating social media topics and scheduling.
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    - **Validation**: Plan must be in 'pending_blog_topic_approval' status
    - **Validation**: Number of approved topics must match blog_posts_quota
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
    
    # Check if plan status is correct - allow multiple valid statuses
    valid_statuses = ['pending_blog_topic_approval', 'pending_final_scheduling', 'error']
    if content_plan.status not in valid_statuses:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Content plan must be in one of these statuses: {', '.join(valid_statuses)}. Current status: {content_plan.status}"
        )
    
    # Count approved topics
    approved_topics_count = crud.suggested_topic_crud.count_by_status(
        db, content_plan.id, "approved"
    )
    
    # Check if there is at least one approved topic
    if approved_topics_count < 1:
        raise HTTPException(
            status_code=http_status.HTTP_409_CONFLICT,
            detail=f"No approved topics found. Please approve at least 1 topic to continue."
        )
    
    # Log warning if approved topics count is less than quota
    if approved_topics_count < content_plan.blog_posts_quota:
        logger.warning(f"Approved topics ({approved_topics_count}) is less than quota ({content_plan.blog_posts_quota}) for plan {plan_id}")
    
    try:
        # Update plan status to generating_sm_topics
        content_plan.status = 'generating_sm_topics'
        content_plan.updated_at = datetime.utcnow()
        db.commit()
        
        # Trigger the Celery task chain for SM generation and scheduling
        from celery import chain
        from app.tasks.main_flow import generate_correlated_sm_variants_task, schedule_final_plan_task
        
        task_chain = chain(
            generate_correlated_sm_variants_task.s(plan_id),
            schedule_final_plan_task.s(plan_id)
        )
        task = task_chain.apply_async()
        
        logger.info(f"Started SM generation chain for plan {plan_id}, task_id: {task.id}")
        
        return {
            "status": "ACCEPTED",
            "message": "Social media generation process started successfully",
            "plan_id": plan_id,
            "task_id": task.id,
            "current_status": "generating_sm_topics",
            "approved_topics_count": approved_topics_count,
            "blog_posts_quota": content_plan.blog_posts_quota,
            "next_steps": [
                "1. Generate social media topics based on approved blog topics",
                "2. Create scheduling recommendations",
                "3. Update plan status to 'complete'"
            ]
        }
        
    except Exception as e:
        # Rollback plan status on error
        try:
            content_plan.status = 'pending_blog_topic_approval'
            content_plan.updated_at = datetime.utcnow()
            db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting social media generation: {str(e)}"
        )


@router.post("/content-plans/{plan_id}/regenerate-blog-topics", status_code=http_status.HTTP_202_ACCEPTED)
async def regenerate_blog_topics(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenerate blog topics for a content plan.
    
    This endpoint allows regenerating blog topics when the current suggestions are not satisfactory.
    It marks all existing topics as rejected and generates new ones.
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
    - **Validation**: Plan must be in 'pending_blog_topic_approval' status
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
    
    # Check if plan status is correct
    if content_plan.status != 'pending_blog_topic_approval':
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Content plan must be in 'pending_blog_topic_approval' status. Current status: {content_plan.status}"
        )
    
    try:
        # Mark all existing topics as rejected
        existing_topics = crud.suggested_topic_crud.get_by_content_plan_id(db, plan_id)
        for topic in existing_topics:
            if topic.status == 'suggested':
                topic.status = 'rejected'
                topic.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Update plan status to generating_topics
        content_plan.status = 'generating_topics'
        content_plan.updated_at = datetime.utcnow()
        db.commit()
        
        # Trigger the Celery task chain for regeneration
        from celery import chain
        from app.tasks.main_flow import contextualize_task, generate_and_save_blog_topics_task
        
        task_chain = chain(
            contextualize_task.s(plan_id),
            generate_and_save_blog_topics_task.s(plan_id)
        )
        task = task_chain.apply_async()
        
        logger.info(f"Started blog topics regeneration for plan {plan_id}, task_id: {task.id}")
        
        rejected_count = len([t for t in existing_topics if t.status == 'rejected'])
        
        return {
            "status": "ACCEPTED",
            "message": "Blog topics regeneration started successfully",
            "plan_id": plan_id,
            "task_id": task.id,
            "current_status": "generating_topics",
            "rejected_topics_count": rejected_count,
            "blog_posts_quota": content_plan.blog_posts_quota,
            "next_steps": [
                "1. Contextualize strategy and previous topics",
                "2. Generate new blog topics avoiding rejected ones",
                "3. Update plan status to 'pending_blog_topic_approval'"
            ]
        }
        
    except Exception as e:
        # Rollback plan status on error
        try:
            content_plan.status = 'pending_blog_topic_approval'
            content_plan.updated_at = datetime.utcnow()
            db.commit()
        except:
            pass
        
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting blog topics regeneration: {str(e)}"
        )


@router.post("/content-plans/{plan_id}/regenerate-all-content", status_code=http_status.HTTP_202_ACCEPTED)
async def regenerate_all_content(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Regenerate all content for a content plan.
    
    This endpoint regenerates the entire content plan from scratch, keeping the same settings
    but generating new topics and content.
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 202 Accepted with task ID
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
    
    try:
        # Mark all existing topics as inactive
        existing_topics = crud.suggested_topic_crud.get_by_content_plan_id(db, plan_id)
        for topic in existing_topics:
            topic.is_active = False
            topic.updated_at = datetime.utcnow()
        
        # Mark all content drafts as inactive
        from app.db.models import ContentDraft, ContentVariant
        drafts = db.query(ContentDraft).join(
            ContentDraft.suggested_topic
        ).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).all()
        
        for draft in drafts:
            draft.is_active = False
            draft.updated_at = datetime.utcnow()
            # Also mark variants as inactive
            for variant in draft.variants:
                variant.is_active = False
                variant.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Reset plan status to new
        content_plan.status = 'new'
        content_plan.updated_at = datetime.utcnow()
        db.commit()
        
        # Trigger the full generation chain
        from celery import chain
        from app.tasks.main_flow import contextualize_task, generate_and_save_blog_topics_task
        
        task_chain = chain(
            contextualize_task.s(plan_id),
            generate_and_save_blog_topics_task.s(plan_id)
        )
        task = task_chain.apply_async()
        
        logger.info(f"Started full content regeneration for plan {plan_id}, task_id: {task.id}")
        
        return {
            "status": "ACCEPTED",
            "message": "Content regeneration started successfully",
            "plan_id": plan_id,
            "task_id": task.id,
            "current_status": "generating_topics",
            "blog_posts_quota": content_plan.blog_posts_quota,
            "sm_posts_quota": content_plan.sm_posts_quota,
            "deactivated_topics": len(existing_topics),
            "deactivated_drafts": len(drafts),
            "next_steps": [
                "1. Generate new blog topics",
                "2. Approve topics",
                "3. Generate social media content",
                "4. Complete scheduling"
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting content regeneration: {str(e)}"
        )


@router.delete("/content-plans/{plan_id}/delete-generated-content", status_code=http_status.HTTP_200_OK)
async def delete_generated_content(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete all generated content for a content plan.
    
    This endpoint removes all generated topics, drafts, and variants for a content plan,
    but keeps the plan itself.
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 200 OK with deletion summary
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
    
    try:
        from app.db.models import ContentDraft, ContentVariant, SuggestedTopic
        
        # Count items before deletion
        topics_count = db.query(SuggestedTopic).filter(
            SuggestedTopic.content_plan_id == plan_id
        ).count()
        
        drafts_count = db.query(ContentDraft).join(
            ContentDraft.suggested_topic
        ).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).count()
        
        variants_count = db.query(ContentVariant).join(
            ContentVariant.draft
        ).join(
            ContentDraft.suggested_topic
        ).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).count()
        
        # Delete content variants first (due to foreign key constraints)
        db.query(ContentVariant).filter(
            ContentVariant.draft.has(
                ContentDraft.suggested_topic.has(content_plan_id=plan_id)
            )
        ).delete(synchronize_session=False)
        
        # Delete content drafts
        db.query(ContentDraft).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).delete(synchronize_session=False)
        
        # Delete suggested topics
        db.query(SuggestedTopic).filter(
            SuggestedTopic.content_plan_id == plan_id
        ).delete(synchronize_session=False)
        
        # Reset plan status to new
        content_plan.status = 'new'
        content_plan.updated_at = datetime.utcnow()
        
        db.commit()
        
        logger.info(f"Deleted all content for plan {plan_id}: {topics_count} topics, {drafts_count} drafts, {variants_count} variants")
        
        return {
            "status": "SUCCESS",
            "message": "All generated content deleted successfully",
            "plan_id": plan_id,
            "deleted": {
                "topics": topics_count,
                "drafts": drafts_count,
                "variants": variants_count
            },
            "plan_status": "new"
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting generated content: {str(e)}"
        )


@router.delete("/content-plans/{plan_id}/hard-delete", status_code=http_status.HTTP_200_OK)
async def hard_delete_content_plan(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Permanently delete a content plan and all associated data.
    
    This endpoint performs a hard delete of the content plan and all related data including
    topics, drafts, variants, briefs, and correlation rules.
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: 200 OK with deletion summary
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
    
    try:
        from app.db.models import (
            ContentDraft, ContentVariant, SuggestedTopic, 
            ContentBrief, ContentCorrelationRule, ScheduledPost
        )
        
        # Count all related items
        topics_count = db.query(SuggestedTopic).filter(
            SuggestedTopic.content_plan_id == plan_id
        ).count()
        
        drafts_count = db.query(ContentDraft).join(
            ContentDraft.suggested_topic
        ).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).count()
        
        variants_count = db.query(ContentVariant).join(
            ContentVariant.draft
        ).join(
            ContentDraft.suggested_topic
        ).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).count()
        
        briefs_count = db.query(ContentBrief).filter(
            ContentBrief.content_plan_id == plan_id
        ).count()
        
        scheduled_posts_count = db.query(ScheduledPost).filter(
            ScheduledPost.content_plan_id == plan_id
        ).count()
        
        # Delete in correct order due to foreign key constraints
        
        # 1. Delete content variants
        db.query(ContentVariant).filter(
            ContentVariant.draft.has(
                ContentDraft.suggested_topic.has(content_plan_id=plan_id)
            )
        ).delete(synchronize_session=False)
        
        # 2. Delete content drafts
        db.query(ContentDraft).filter(
            ContentDraft.suggested_topic.has(content_plan_id=plan_id)
        ).delete(synchronize_session=False)
        
        # 3. Delete scheduled posts
        db.query(ScheduledPost).filter(
            ScheduledPost.content_plan_id == plan_id
        ).delete(synchronize_session=False)
        
        # 4. Delete suggested topics
        db.query(SuggestedTopic).filter(
            SuggestedTopic.content_plan_id == plan_id
        ).delete(synchronize_session=False)
        
        # 5. Delete content briefs
        db.query(ContentBrief).filter(
            ContentBrief.content_plan_id == plan_id
        ).delete(synchronize_session=False)
        
        # 6. Delete correlation rules
        db.query(ContentCorrelationRule).filter(
            ContentCorrelationRule.content_plan_id == plan_id
        ).delete(synchronize_session=False)
        
        # 7. Finally delete the content plan itself
        db.delete(content_plan)
        
        db.commit()
        
        logger.info(f"Hard deleted content plan {plan_id} and all related data")
        
        return {
            "status": "SUCCESS",
            "message": "Content plan and all related data permanently deleted",
            "plan_id": plan_id,
            "deleted": {
                "content_plan": 1,
                "topics": topics_count,
                "drafts": drafts_count,
                "variants": variants_count,
                "briefs": briefs_count,
                "scheduled_posts": scheduled_posts_count
            }
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting content plan: {str(e)}"
        )


@router.get("/content-plans/{plan_id}/full-content")
async def get_content_plan_full_content(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get full content visualization data for a content plan.
    
    Returns organized content with blog posts and their related social media posts,
    plus any standalone social media posts.
    
    - **plan_id**: ID of the content plan
    - **Requires authentication**: User must be logged in
    - **Authorization**: User must have access to the organization
    - **Returns**: Organized content data for visualization
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
    
    try:
        from app.db.models import SuggestedTopic, ContentDraft, ContentVariant
        from sqlalchemy.orm import joinedload
        
        # Get all blog topics with their drafts and variants
        blog_topics = db.query(SuggestedTopic).options(
            joinedload(SuggestedTopic.content_drafts).joinedload(ContentDraft.variants)
        ).filter(
            SuggestedTopic.content_plan_id == plan_id,
            SuggestedTopic.category == "blog",
            SuggestedTopic.status == "approved",
            SuggestedTopic.is_active == True
        ).all()
        
        # Get all social media topics
        sm_topics = db.query(SuggestedTopic).options(
            joinedload(SuggestedTopic.content_drafts).joinedload(ContentDraft.variants),
            joinedload(SuggestedTopic.parent)
        ).filter(
            SuggestedTopic.content_plan_id == plan_id,
            SuggestedTopic.category == "social_media",
            SuggestedTopic.is_active == True
        ).all()
        
        # Organize content by blog posts with their related SM posts
        organized_content = []
        for blog_topic in blog_topics:
            blog_data = {
                "blog_post": {
                    "id": blog_topic.id,
                    "topic": {
                        "id": blog_topic.id,
                        "title": blog_topic.title,
                        "description": blog_topic.description
                    },
                    "created_at": blog_topic.created_at.isoformat() if blog_topic.created_at else None,
                    "drafts": [],
                    "variants": []
                },
                "related_social_posts": []
            }
            
            # Add blog drafts and variants
            for draft in blog_topic.content_drafts:
                if draft.is_active:
                    draft_data = {
                        "id": draft.id,
                        "status": draft.status,
                        "created_at": draft.created_at.isoformat() if draft.created_at else None
                    }
                    blog_data["blog_post"]["drafts"].append(draft_data)
                    
                    # Add variants
                    for variant in draft.variants:
                        if variant.is_active:
                            variant_data = {
                                "id": variant.id,
                                "platform_name": variant.platform_name,
                                "content_text": variant.content_text,
                                "status": variant.status,
                                "created_at": variant.created_at.isoformat() if variant.created_at else None
                            }
                            blog_data["blog_post"]["variants"].append(variant_data)
            
            # Find related SM posts
            related_sm = [sm for sm in sm_topics if sm.parent_topic_id == blog_topic.id]
            for sm_topic in related_sm:
                sm_post_data = {
                    "id": sm_topic.id,
                    "topic": {
                        "id": sm_topic.id,
                        "title": sm_topic.title,
                        "description": sm_topic.description
                    },
                    "created_at": sm_topic.created_at.isoformat() if sm_topic.created_at else None,
                    "drafts": [],
                    "variants": []
                }
                
                # Add SM drafts and variants
                for draft in sm_topic.content_drafts:
                    if draft.is_active:
                        draft_data = {
                            "id": draft.id,
                            "status": draft.status,
                            "created_at": draft.created_at.isoformat() if draft.created_at else None
                        }
                        sm_post_data["drafts"].append(draft_data)
                        
                        # Add variants
                        for variant in draft.variants:
                            if variant.is_active:
                                variant_data = {
                                    "id": variant.id,
                                    "platform_name": variant.platform_name,
                                    "content_text": variant.content_text,
                                    "status": variant.status,
                                    "created_at": variant.created_at.isoformat() if variant.created_at else None
                                }
                                sm_post_data["variants"].append(variant_data)
                
                blog_data["related_social_posts"].append(sm_post_data)
            
            organized_content.append(blog_data)
        
        # Get standalone social media posts (those without parent_topic_id)
        standalone_social_posts = []
        standalone_sm = [sm for sm in sm_topics if sm.parent_topic_id is None]
        for sm_topic in standalone_sm:
            sm_post_data = {
                "id": sm_topic.id,
                "topic": {
                    "id": sm_topic.id,
                    "title": sm_topic.title,
                    "description": sm_topic.description
                },
                "created_at": sm_topic.created_at.isoformat() if sm_topic.created_at else None,
                "drafts": [],
                "variants": []
            }
            
            # Add SM drafts and variants
            for draft in sm_topic.content_drafts:
                if draft.is_active:
                    draft_data = {
                        "id": draft.id,
                        "status": draft.status,
                        "created_at": draft.created_at.isoformat() if draft.created_at else None
                    }
                    sm_post_data["drafts"].append(draft_data)
                    
                    # Add variants
                    for variant in draft.variants:
                        if variant.is_active:
                            variant_data = {
                                "id": variant.id,
                                "platform_name": variant.platform_name,
                                "content_text": variant.content_text,
                                "status": variant.status,
                                "created_at": variant.created_at.isoformat() if variant.created_at else None
                            }
                            sm_post_data["variants"].append(variant_data)
            
            standalone_social_posts.append(sm_post_data)
        
        # Calculate statistics
        statistics = {
            "total_blog_posts": len(blog_topics),
            "total_social_posts": len(sm_topics),
            "correlated_social_posts": len([sm for sm in sm_topics if sm.parent_topic_id is not None]),
            "standalone_social_posts": len(standalone_sm)
        }
        
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
            "statistics": statistics
        }
        
    except Exception as e:
        logger.error(f"Error getting full content for plan {plan_id}: {str(e)}")
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving content: {str(e)}"
        ) 