#!/usr/bin/env python3
"""Check draft and variant status"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentDraft, ContentVariant, SuggestedTopic

db = SessionLocal()

# Get recent drafts
drafts = db.query(ContentDraft).order_by(ContentDraft.created_at.desc()).limit(10).all()

print(f"=== ANALIZA {len(drafts)} NAJNOWSZYCH DRAFTÓW ===\n")

drafts_with_variants = 0
drafts_without_variants = 0

for draft in drafts:
    topic = draft.suggested_topic
    variants = db.query(ContentVariant).filter(ContentVariant.content_draft_id == draft.id).all()
    
    print(f"Draft ID: {draft.id}")
    print(f"Topic: {topic.title[:60]}...")
    print(f"Category: {topic.category}")
    print(f"Status: {draft.status}")
    print(f"Variants: {len(variants)}")
    
    if variants:
        drafts_with_variants += 1
        for v in variants:
            print(f"  - Platform: {v.platform_name}, Status: {v.status}")
    else:
        drafts_without_variants += 1
        print("  ❌ BRAK WARIANTÓW")
    
    print()

print(f"\n=== PODSUMOWANIE ===")
print(f"Drafty z wariantami: {drafts_with_variants}")
print(f"Drafty bez wariantów: {drafts_without_variants}")

# Check draft statuses
statuses = db.query(ContentDraft.status, db.func.count(ContentDraft.id))\
    .group_by(ContentDraft.status).all()

print(f"\n=== STATUSY DRAFTÓW ===")
for status, count in statuses:
    print(f"{status}: {count}")

db.close()