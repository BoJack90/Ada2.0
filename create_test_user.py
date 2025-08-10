#!/usr/bin/env python3
"""Script to create test user 'essa' with password 'Haslo123!'"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db import models, schemas, crud
from app.db.models import Base

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

def create_test_user():
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = crud.user_crud.get_by_username(db, "essa")
        if existing_user:
            print("User 'essa' already exists")
            return
        
        # Create user
        user_data = schemas.UserCreate(
            username="essa",
            email="essa@example.com",
            password="Haslo123!",
            first_name="Test",
            last_name="User"
        )
        
        user = crud.user_crud.create(db, user_data)
        print(f"Created user: {user.username} ({user.email})")
        
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()