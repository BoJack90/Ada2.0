#!/usr/bin/env python3
"""Re-analyze brief to debug hallucination issue"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief
import base64

# Get brief from database
db = SessionLocal()
brief = db.query(ContentBrief).filter(ContentBrief.id == 6).first()

if brief and brief.file_path:
    print(f"Brief ID: {brief.id}")
    print(f"File path: {brief.file_path}")
    print(f"Current extracted content length: {len(brief.extracted_content) if brief.extracted_content else 0}")
    
    # Clear existing analysis to force re-analysis
    brief.ai_analysis = None
    brief.key_topics = []
    db.commit()
    print("Cleared existing analysis")
    
    # Trigger re-analysis
    from app.tasks.brief_analysis import analyze_brief_task
    
    with open(brief.file_path, 'rb') as f:
        file_content_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    result = analyze_brief_task.delay(
        brief_id=brief.id,
        file_content_b64=file_content_b64,
        file_mime_type="application/pdf"
    )
    
    print(f"Triggered re-analysis task: {result.id}")
else:
    print("Brief not found")

db.close()