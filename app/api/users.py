from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, schemas, models
from app.core.dependencies import get_current_active_user

router = APIRouter()

@router.get("/me", response_model=schemas.User)
def get_current_user_info(current_user: models.User = Depends(get_current_active_user)):
    """Get current user information"""
    return current_user

@router.put("/me", response_model=schemas.User)
def update_current_user(
    user_update: schemas.UserUpdate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    update_data = user_update.dict(exclude_unset=True)
    
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/organizations", response_model=List[schemas.Organization])
def get_user_organizations(
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's organizations"""
    return crud.organization_crud.get_user_organizations(db, current_user.id)

@router.get("/tasks", response_model=List[schemas.TaskWithDetails])
def get_user_tasks(
    org_id: int = None,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's assigned tasks"""
    # If org_id provided, check access
    if org_id and not crud.organization_crud.user_has_access(db, org_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return crud.task_crud.get_user_tasks(db, current_user.id, org_id)
