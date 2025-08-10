#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentBrief
import base64

# Re-analyze brief with updated prompt
db = SessionLocal()
brief = db.query(ContentBrief).filter(ContentBrief.id == 6).first()

if brief:
    print(f"Re-analyzing brief {brief.id} with updated prompt...")
    
    # Clear current analysis
    brief.ai_analysis = None
    brief.key_topics = []
    db.commit()
    
    # Trigger new analysis
    from app.tasks.brief_analysis import analyze_brief_task
    
    with open(brief.file_path, 'rb') as f:
        file_content_b64 = base64.b64encode(f.read()).decode('utf-8')
    
    result = analyze_brief_task.delay(
        brief_id=brief.id,
        file_content_b64=file_content_b64,
        file_mime_type="application/pdf"
    )
    
    print(f"Task ID: {result.id}")
    print("Check Redis for task status...")

db.close()