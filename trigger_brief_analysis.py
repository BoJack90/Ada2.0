#!/usr/bin/env python3
"""Trigger brief analysis for existing brief"""
import base64
from app.tasks.brief_analysis import analyze_brief_task

# Brief details
brief_id = 6
file_path = "/app/uploads/briefs/1a7cedfa-b2bf-4aa2-84dc-22ef4eef6589.pdf"

# Read file and encode
with open(file_path, 'rb') as f:
    file_content_b64 = base64.b64encode(f.read()).decode('utf-8')

# Trigger analysis
result = analyze_brief_task.delay(
    brief_id=brief_id,
    file_content_b64=file_content_b64,
    file_mime_type="application/pdf"
)

print(f"Triggered analysis task: {result.id}")