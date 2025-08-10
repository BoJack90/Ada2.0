from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List
import logging
from app.db.database import get_db
from app.schemas.organization import OrganizationCreate, OrganizationUpdate, OrganizationResponse
from app.db import crud
from app.core.dependencies import get_current_active_user
from app.db.models import User

logger = logging.getLogger(__name__)
router = APIRouter(tags=["organizations"])


@router.post("/", response_model=OrganizationResponse, status_code=201)
def create_organization(
    organization: OrganizationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tworzy nową organizację"""
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info(f"[CREATE_ORG] Received organization data: {organization.dict()}")
    logger.info(f"[CREATE_ORG] Current user: {current_user.username} (ID: {current_user.id})")
    
    try:
        # Use the current authenticated user as owner
        result = crud.organization_crud.create(db=db, org_create=organization, owner_id=current_user.id)
        logger.info(f"[CREATE_ORG] Successfully created organization: {result.name} (ID: {result.id})")
        
        # Trigger website analysis if website URL is provided
        if organization.website:
            from app.tasks.website_analysis import analyze_organization_website_task
            
            logger.info(f"[CREATE_ORG] Triggering website analysis for: {organization.website}")
            analyze_organization_website_task.delay(
                organization_id=result.id,
                website_url=organization.website,
                organization_name=result.name
            )
        
        return result
    except Exception as e:
        logger.error(f"[CREATE_ORG] Error creating organization: {str(e)}")
        logger.error(f"[CREATE_ORG] Exception type: {type(e).__name__}")
        import traceback
        logger.error(f"[CREATE_ORG] Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=400, detail=f"Błąd podczas tworzenia organizacji: {str(e)}")


@router.get("/", response_model=List[OrganizationResponse])
def get_organizations(
    skip: int = Query(0, ge=0, description="Liczba organizacji do pominięcia"),
    limit: int = Query(100, ge=1, le=1000, description="Maksymalna liczba organizacji do pobrania"),
    search: str = Query(None, description="Wyszukiwanie po nazwie organizacji"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera listę organizacji użytkownika"""
    # Return only organizations the user has access to
    return crud.organization_crud.get_user_organizations(db, current_user.id)


@router.get("/{organization_id}", response_model=OrganizationResponse)
def get_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera organizację po ID"""
    # Check if user has access to this organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(status_code=403, detail="You don't have access to this organization")
    
    organization = crud.organization_crud.get_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organizacja nie została znaleziona")
    return organization


@router.put("/{organization_id}", response_model=OrganizationResponse)
def update_organization(
    organization_id: int,
    organization_update: OrganizationUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aktualizuje organizację"""
    # Check if user has access to this organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(status_code=403, detail="You don't have access to this organization")
    
    # Check if organization exists
    organization = crud.organization_crud.get_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organizacja nie została znaleziona")
    
    # Update organization (we'll need to add update method to OrganizationCRUD)
    try:
        # Check if website URL is being updated
        old_website = organization.website
        
        # For now, update manually
        update_data = organization_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(organization, field, value)
        
        db.commit()
        db.refresh(organization)
        
        # Trigger website analysis if website URL changed
        if 'website' in update_data and update_data['website'] != old_website:
            from app.tasks.website_analysis import analyze_organization_website_task
            
            logger.info(f"[UPDATE_ORG] Website changed, triggering analysis for: {organization.website}")
            analyze_organization_website_task.delay(
                organization_id=organization_id,
                website_url=organization.website,
                organization_name=organization.name
            )
        
        return organization
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas aktualizacji organizacji: {str(e)}")


@router.get("/{organization_id}/website-analysis")
def get_website_analysis(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera analizę strony internetowej organizacji"""
    # Check if user has access to this organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(status_code=403, detail="You don't have access to this organization")
    
    # Get website analysis
    from app.db.models import WebsiteAnalysis
    analysis = db.query(WebsiteAnalysis).filter(
        WebsiteAnalysis.organization_id == organization_id
    ).first()
    
    if not analysis:
        return {
            "status": "not_found",
            "message": "No website analysis found for this organization"
        }
    
    return {
        "status": analysis.analysis_status,
        "website_url": analysis.website_url,
        "industry_detected": analysis.industry_detected,
        "services_detected": analysis.services_detected,
        "company_values": analysis.company_values,
        "target_audience": analysis.target_audience,
        "content_tone": analysis.content_tone,
        "key_topics": analysis.key_topics,
        "competitors_mentioned": analysis.competitors_mentioned,
        "last_analysis_date": analysis.last_analysis_date,
        "error_message": analysis.error_message
    }


@router.post("/{organization_id}/website-analysis/refresh")
def refresh_website_analysis(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Odświeża analizę strony internetowej organizacji"""
    # Check if user has access to this organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(status_code=403, detail="You don't have access to this organization")
    
    # Get organization
    organization = crud.organization_crud.get_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    if not organization.website:
        raise HTTPException(status_code=400, detail="Organization has no website URL")
    
    # Trigger refresh
    from app.tasks.website_analysis import analyze_organization_website_task
    
    task = analyze_organization_website_task.delay(
        organization_id=organization_id,
        website_url=organization.website,
        organization_name=organization.name
    )
    
    return {
        "status": "triggered",
        "task_id": task.id,
        "message": "Website analysis refresh has been triggered"
    }


@router.post("/{organization_id}/website-analysis/cancel")
async def cancel_website_analysis(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Cancel ongoing website analysis for an organization
    """
    from app.db.models import WebsiteAnalysis, Organization
    from datetime import datetime
    
    # Check if organization exists and user has access
    organization = db.query(Organization).filter(
        Organization.id == organization_id,
        Organization.is_active == True
    ).first()
    
    if not organization:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Update website analysis status to cancelled
    website_analysis = db.query(WebsiteAnalysis).filter(
        WebsiteAnalysis.organization_id == organization_id
    ).first()
    
    if website_analysis and website_analysis.analysis_status == 'processing':
        website_analysis.analysis_status = 'cancelled'
        website_analysis.error_message = 'Analysis cancelled by user'
        website_analysis.updated_at = datetime.utcnow()
        db.commit()
        
        return {
            "message": "Website analysis cancelled",
            "organization_id": organization_id,
            "status": "cancelled"
        }
    
    return {
        "message": "No active analysis to cancel",
        "organization_id": organization_id,
        "status": "no_active_analysis"
    }


@router.delete("/{organization_id}", status_code=204)
def delete_organization(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Usuwa organizację"""
    # Check if user has access to this organization
    if not crud.organization_crud.user_has_access(db, organization_id, current_user.id):
        raise HTTPException(status_code=403, detail="You don't have access to this organization")
    
    # Check if organization exists
    organization = crud.organization_crud.get_by_id(db, organization_id)
    if not organization:
        raise HTTPException(status_code=404, detail="Organizacja nie została znaleziona")
    
    # Delete organization
    try:
        db.delete(organization)
        db.commit()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd podczas usuwania organizacji: {str(e)}")
