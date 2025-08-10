from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, schemas, models
from app.core.dependencies import get_current_active_user, get_organization_access

router = APIRouter()

@router.get("/", response_model=List[schemas.Project])
def get_projects(
    org_id: int,
    organization: models.Organization = Depends(get_organization_access),
    db: Session = Depends(get_db)
):
    """Get organization projects"""
    return crud.project_crud.get_organization_projects(db, org_id)

@router.post("/", response_model=schemas.Project)
def create_project(
    project: schemas.ProjectCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new project"""
    # Check organization access
    organization = crud.organization_crud.get_by_id(db, project.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if not crud.organization_crud.user_has_access(db, project.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return crud.project_crud.create(db, project)

@router.get("/{project_id}", response_model=schemas.Project)
def get_project(
    project_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get project by ID"""
    project = crud.project_crud.get_by_id(db, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found"
        )
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, project.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return project
