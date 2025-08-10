from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.database import get_db
from app.db import crud, schemas
from app.core.security import create_access_token
from app.core.config import settings
from app.core.rate_limit import limiter

router = APIRouter()

@router.post("/register", response_model=schemas.User)
@limiter.limit("5/minute")
def register(request: Request, user_create: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register new user"""
    # Check if user already exists
    if crud.user_crud.get_by_email(db, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if crud.user_crud.get_by_username(db, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    user = crud.user_crud.create(db, user_create)
    return user

@router.post("/login", response_model=schemas.Token)
@limiter.limit("5/minute")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Login user"""
    user = crud.user_crud.authenticate(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login
    crud.user_crud.update_last_login(db, user)
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login-json", response_model=schemas.Token)
@limiter.limit("5/minute")
def login_json(request: Request, login_request: schemas.LoginRequest, db: Session = Depends(get_db)):
    """Login user with JSON payload"""
    user = crud.user_crud.authenticate(db, login_request.username, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    # Update last login
    crud.user_crud.update_last_login(db, user)
    
    return {"access_token": access_token, "token_type": "bearer"}
