from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db import crud, models
from app.core.security import verify_token
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> models.User:
    """Get current authenticated user"""
    print(f"[DEBUG] Received credentials: {credentials.credentials[:50]}..." if credentials.credentials else "No credentials")
    
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    username = verify_token(credentials.credentials)
    print(f"[DEBUG] Verified username: {username}")
    
    if username is None:
        print("[DEBUG] Token verification failed")
        raise credentials_exception
    
    user = crud.user_crud.get_by_username(db, username)
    print(f"[DEBUG] Found user: {user.username if user else 'None'}")
    
    if user is None:
        print("[DEBUG] User not found in database")
        raise credentials_exception
    
    return user

def get_current_active_user(
    current_user: models.User = Depends(get_current_user)
) -> models.User:
    """Get current active user"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

def get_organization_access(
    org_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> models.Organization:
    """Check if user has access to organization"""
    organization = crud.organization_crud.get_by_id(db, org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if not crud.organization_crud.user_has_access(db, org_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    
    return organization


# AI System Dependencies
def get_prompt_manager(db: Session = Depends(get_db)) -> PromptManager:
    """
    Dependency provider dla PromptManager.
    Tworzy instancję PromptManager z aktualną sesją bazy danych.
    """
    return PromptManager(db_session=db)


def get_ai_config_service(db: Session = Depends(get_db)) -> AIConfigService:
    """
    Dependency provider dla AIConfigService.
    Tworzy instancję AIConfigService z aktualną sesją bazy danych.
    """
    return AIConfigService(db_session=db)

def require_organization_owner(
    org_id: int,
    current_user: models.User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> models.Organization:
    """Check if user is organization owner"""
    organization = crud.organization_crud.get_by_id(db, org_id)
    if not organization:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Organization not found"
        )
    
    if organization.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only organization owner can perform this action"
        )
    
    return organization
