from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import crud, schemas, models
from app.core.dependencies import get_current_active_user, get_organization_access

router = APIRouter()

@router.get("/", response_model=List[schemas.TaskWithDetails])
def get_tasks(
    org_id: int = Query(..., description="Organization ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    assignee_id: Optional[int] = Query(None, description="Filter by assignee"),
    project_id: Optional[int] = Query(None, description="Filter by project"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign"),
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get tasks for organization with filters"""
    # Check organization access
    if not crud.organization_crud.user_has_access(db, org_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return crud.task_crud.get_organization_tasks(
        db, org_id, status, assignee_id, project_id, campaign_id
    )

@router.post("/", response_model=schemas.TaskWithDetails)
def create_task(
    task: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new task"""
    # Check organization access
    if not crud.organization_crud.user_has_access(db, task.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate project and campaign belong to organization
    if task.project_id:
        project = crud.project_crud.get_by_id(db, task.project_id)
        if not project or project.organization_id != task.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project does not belong to this organization"
            )
    
    if task.campaign_id:
        campaign = crud.campaign_crud.get_by_id(db, task.campaign_id)
        if not campaign or campaign.organization_id != task.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Campaign does not belong to this organization"
            )
    
    # Validate assignee has access to organization
    if task.assignee_id:
        if not crud.organization_crud.user_has_access(db, task.organization_id, task.assignee_id):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee does not have access to this organization"
            )
    
    db_task = crud.task_crud.create(db, task, current_user.id)
    return crud.task_crud.get_by_id(db, db_task.id)

@router.get("/{task_id}", response_model=schemas.TaskWithDetails)
def get_task(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get task by ID"""
    task = crud.task_crud.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, task.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return task

@router.put("/{task_id}", response_model=schemas.TaskWithDetails)
def update_task(
    task_id: int,
    task_update: schemas.TaskUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update task"""
    task = crud.task_crud.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, task.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate assignee has access to organization if changing assignee
    if task_update.assignee_id is not None:
        if task_update.assignee_id and not crud.organization_crud.user_has_access(
            db, task.organization_id, task_update.assignee_id
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Assignee does not have access to this organization"
            )
    
    updated_task = crud.task_crud.update(db, task_id, task_update)
    return crud.task_crud.get_by_id(db, updated_task.id)

@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete task"""
    task = crud.task_crud.get_by_id(db, task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, task.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Only creator or organization owner can delete
    organization = crud.organization_crud.get_by_id(db, task.organization_id)
    if task.created_by_id != current_user.id and organization.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only task creator or organization owner can delete tasks"
        )
    
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
