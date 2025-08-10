#!/usr/bin/env python3
"""Check the brief analysis results"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief
import json

# Get brief from database
db = SessionLocal()
brief = db.query(ContentBrief).filter(ContentBrief.id == 6).first()

if brief:
    print(f"Brief ID: {brief.id}")
    print(f"File path: {brief.file_path}")
    print(f"Key topics: {brief.key_topics}")
    
    if brief.ai_analysis:
        print("\n=== AI ANALYSIS ===")
        print(json.dumps(brief.ai_analysis, indent=2, ensure_ascii=False))
        
        # Check for hallucination keywords
        analysis_str = json.dumps(brief.ai_analysis).lower()
        print("\n=== HALLUCINATION CHECK ===")
        print(f"Contains 'sztuczna inteligencja': {'sztuczna inteligencja' in analysis_str}")
        print(f"Contains 'ai': {'ai' in analysis_str}")
        print(f"Contains 'machine learning': {'machine learning' in analysis_str}")
        print(f"Contains 'uczenie maszynowe': {'uczenie maszynowe' in analysis_str}")
        
        # Check for real content
        print("\n=== REAL CONTENT CHECK ===")
        print(f"Contains 'monitoring': {'monitoring' in analysis_str}")
        print(f"Contains 'energia': {'energia' in analysis_str}")
        print(f"Contains 'cfd': {'cfd' in analysis_str}")
        print(f"Contains 'smart': {'smart' in analysis_str}")
    else:
        print("No AI analysis found")
else:
    print("Brief not found")

db.close()