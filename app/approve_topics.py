#!/usr/bin/env python3
"""Approve suggested topics for testing"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic

db = SessionLocal()

# Find suggested topics for plan 6
topics = db.query(SuggestedTopic).filter(
    SuggestedTopic.content_plan_id == 6,
    SuggestedTopic.status == "suggested",
    SuggestedTopic.category == "blog"
).limit(4).all()

print(f"Found {len(topics)} suggested topics to approve")

for topic in topics:
    print(f"\nApproving topic: {topic.title}")
    topic.status = "approved"

db.commit()
print(f"\nApproved {len(topics)} topics")

db.close()