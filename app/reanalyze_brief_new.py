#!/usr/bin/env python3
"""Re-analyze brief with updated prompt"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief
import base64

db = SessionLocal()

# Get the latest brief
brief = db.query(ContentBrief).order_by(ContentBrief.created_at.desc()).first()

if brief and brief.file_path:
    print(f"Re-analyzing brief ID: {brief.id}")
    print(f"Plan ID: {brief.content_plan_id}")
    
    # Clear existing analysis to force re-analysis
    brief.ai_analysis = None
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
    print("Wait a moment and check the results...")
else:
    print("Brief not found")

db.close()