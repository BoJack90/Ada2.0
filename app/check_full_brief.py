#!/usr/bin/env python3
"""Check full brief text"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief

db = SessionLocal()

brief = db.query(ContentBrief).order_by(ContentBrief.created_at.desc()).first()

if brief and brief.extracted_content:
    print("=== PEŁNA TREŚĆ BRIEFU ===")
    print(brief.extracted_content[:2000])
    
    # Search for Natalia
    if "Dołączyła do nas Natalia Szarach" in brief.extracted_content:
        print("\n\n✓ ZNALEZIONO: 'Dołączyła do nas Natalia Szarach'")
        
        # Find the full context
        start = brief.extracted_content.find("Dołączyła do nas")
        if start != -1:
            end = brief.extracted_content.find("Stanowisko:", start) + 100
            print("\n=== KONTEKST ===")
            print(brief.extracted_content[start:end])

db.close()