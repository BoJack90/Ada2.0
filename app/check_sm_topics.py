#!/usr/bin/env python3
"""Check generated SM topics"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic
import json

db = SessionLocal()

# Find SM topics for content plan 6
sm_topics = db.query(SuggestedTopic).filter(
    SuggestedTopic.content_plan_id == 6,
    SuggestedTopic.category == "social_media"
).order_by(SuggestedTopic.created_at.desc()).limit(20).all()

print(f"Found {len(sm_topics)} SM topics for content plan 6\n")

for i, topic in enumerate(sm_topics, 1):
    print(f"\n=== SM TOPIC {i} ===")
    print(f"ID: {topic.id}")
    print(f"Title: {topic.title}")
    print(f"Description: {topic.description[:150]}..." if len(topic.description) > 150 else topic.description)
    print(f"Status: {topic.status}")
    print(f"Created: {topic.created_at}")
    if topic.meta_data:
        print(f"Meta: {json.dumps(topic.meta_data, indent=2)}")

db.close()