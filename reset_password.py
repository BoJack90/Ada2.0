#!/usr/bin/env python3
"""Script to reset password for user 'essa'"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.db import crud
from app.core.security import get_password_hash

def reset_password():
    db = SessionLocal()
    try:
        # Get user
        user = crud.user_crud.get_by_username(db, "essa")
        if not user:
            print("User 'essa' not found")
            return
        
        # Update password
        new_password_hash = get_password_hash("Haslo123!")
        user.hashed_password = new_password_hash
        db.commit()
        db.refresh(user)
        
        print(f"Password reset successfully for user: {user.username}")
        
    finally:
        db.close()

if __name__ == "__main__":
    reset_password()