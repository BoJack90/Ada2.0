from fastapi import APIRouter, Depends, HTTPException, status as http_status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.db.database import get_db
from app.db import crud
from app.core.dependencies import get_current_active_user
from app.db.models import User, SuggestedTopic
from app.tasks.variant_generation import generate_all_variants_for_topic_task

router = APIRouter()


@router.post("/suggested-topics/{topic_id}/generate-drafts", status_code=http_status.HTTP_202_ACCEPTED)
async def generate_content_drafts(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Uruchamia proces generowania wariantów treści dla zatwierdzonego tematu.
    
    - **topic_id**: ID tematu (SuggestedTopic) do przetworzenia
    - **Requires authentication**: Użytkownik musi być zalogowany
    - **Authorization**: Użytkownik musi mieć dostęp do organizacji tematu
    - **Returns**: task_id dla śledzenia postępu zadania
    
    Status tematu musi być 'approved' aby można było generować treści.
    """
    
    # Pobierz temat z bazy danych
    suggested_topic = db.query(SuggestedTopic).filter(
        SuggestedTopic.id == topic_id
    ).first()
    
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Sprawdź czy użytkownik ma dostęp do organizacji
    if not crud.organization_crud.user_has_access(db, suggested_topic.organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    # Sprawdź czy status tematu to 'approved'
    if suggested_topic.status != "approved":
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail=f"Topic status must be 'approved' to generate drafts. Current status: {suggested_topic.status}"
        )
    
    # Sprawdź czy temat jest aktywny
    if not suggested_topic.is_active:
        raise HTTPException(
            status_code=http_status.HTTP_400_BAD_REQUEST,
            detail="Topic is not active"
        )
    
    try:
        # Uruchom zadanie w tle
        task_result = generate_all_variants_for_topic_task.delay(topic_id)
        
        return {
            "message": "Content variant generation started",
            "task_id": task_result.id,
            "topic_id": topic_id,
            "topic_title": suggested_topic.title,
            "status": "accepted"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error starting content generation task: {str(e)}"
        )


@router.get("/suggested-topics/{topic_id}/generation-status/{task_id}")
async def get_generation_status(
    topic_id: int,
    task_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> Dict[str, Any]:
    """
    Sprawdza status zadania generowania wariantów treści.
    
    - **topic_id**: ID tematu
    - **task_id**: ID zadania Celery
    - **Requires authentication**: Użytkownik musi być zalogowany
    - **Authorization**: Użytkownik musi mieć dostęp do organizacji tematu
    """
    
    # Pobierz temat z bazy danych
    suggested_topic = db.query(SuggestedTopic).filter(
        SuggestedTopic.id == topic_id
    ).first()
    
    if not suggested_topic:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail="Suggested topic not found"
        )
    
    # Sprawdź czy użytkownik ma dostęp do organizacji
    if not crud.organization_crud.user_has_access(db, suggested_topic.organization_id, current_user.id):
        raise HTTPException(
            status_code=http_status.HTTP_403_FORBIDDEN,
            detail="You don't have access to this organization"
        )
    
    try:
        # Sprawdź status zadania Celery
        from app.tasks.celery_app import celery_app
        
        task_result = celery_app.AsyncResult(task_id)
        
        response = {
            "task_id": task_id,
            "topic_id": topic_id,
            "state": task_result.state,
            "ready": task_result.ready()
        }
        
        if task_result.ready():
            if task_result.successful():
                response["result"] = task_result.result
            else:
                response["error"] = str(task_result.info)
        else:
            # Zadanie w toku
            if hasattr(task_result.info, 'get') and task_result.info:
                response["progress"] = task_result.info
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error checking task status: {str(e)}"
        ) 