#!/usr/bin/env python3
"""Test dashboard API response structure"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentDraft, ContentVariant, SuggestedTopic
from sqlalchemy.orm import joinedload
import json

db = SessionLocal()

# Get some drafts with full details
drafts = db.query(ContentDraft).options(
    joinedload(ContentDraft.suggested_topic).joinedload(SuggestedTopic.parent),
    joinedload(ContentDraft.suggested_topic).joinedload(SuggestedTopic.content_plan),
    joinedload(ContentDraft.variants)
).limit(5).all()

print(f"Found {len(drafts)} drafts\n")

for draft in drafts:
    topic = draft.suggested_topic
    print(f"=== DRAFT ID: {draft.id} ===")
    print(f"Topic: {topic.title}")
    print(f"Category: {topic.category}")
    print(f"Plan: {topic.content_plan.plan_period if topic.content_plan else 'N/A'}")
    
    # Check if correlated
    if topic.parent_topic_id:
        print(f"Parent Blog: {topic.parent.title if topic.parent else 'N/A'}")
    
    # Check metadata
    if topic.meta_data:
        print(f"Meta: {json.dumps(topic.meta_data)}")
    
    # Check variants/platforms
    print(f"Variants: {len(draft.variants)}")
    for variant in draft.variants:
        print(f"  - Platform: {variant.platform_name}, Status: {variant.status}")
    
    print()

db.close()