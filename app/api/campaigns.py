from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.db import crud, schemas, models
from app.core.dependencies import get_current_active_user, get_organization_access

router = APIRouter()

@router.get("/", response_model=List[schemas.Campaign])
def get_campaigns(
    org_id: int,
    organization: models.Organization = Depends(get_organization_access),
    db: Session = Depends(get_db)
):
    """Get organization campaigns"""
    return crud.campaign_crud.get_organization_campaigns(db, org_id)

@router.post("/", response_model=schemas.Campaign)
def create_campaign(
    campaign: schemas.CampaignCreate,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create new campaign"""
    # Check organization access
    organization = crud.organization_crud.get_by_id(db, campaign.organization_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if not crud.organization_crud.user_has_access(db, campaign.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    # Validate project belongs to organization if provided
    if campaign.project_id:
        project = crud.project_crud.get_by_id(db, campaign.project_id)
        if not project or project.organization_id != campaign.organization_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Project does not belong to this organization"
            )
    
    return crud.campaign_crud.create(db, campaign)

@router.get("/{campaign_id}", response_model=schemas.Campaign)
def get_campaign(
    campaign_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get campaign by ID"""
    campaign = crud.campaign_crud.get_by_id(db, campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check organization access
    if not crud.organization_crud.user_has_access(db, campaign.organization_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return campaign
