#!/usr/bin/env python3
"""Check generated topics for content plan"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic
import json

# Get topics for content plan
db = SessionLocal()
topics = db.query(SuggestedTopic).filter(SuggestedTopic.content_plan_id == 6).order_by(SuggestedTopic.created_at.desc()).limit(10).all()

print(f"Found {len(topics)} topics for content plan 6\n")

for i, topic in enumerate(topics, 1):
    print(f"\n=== TOPIC {i} ===")
    print(f"ID: {topic.id}")
    print(f"Title: {topic.title}")
    print(f"Description: {topic.description[:200]}..." if len(topic.description) > 200 else topic.description)
    print(f"Category: {topic.category}")
    print(f"Status: {topic.status}")
    print(f"Created: {topic.created_at}")
    if topic.meta_data:
        print(f"Meta data: {json.dumps(topic.meta_data, indent=2)}")

db.close()