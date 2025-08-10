#!/usr/bin/env python3
"""Create drafts for SM topics to make them visible in dashboard"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic, ContentDraft, ContentVariant
from datetime import datetime

db = SessionLocal()

# Find SM topics without drafts
from sqlalchemy import not_, exists

sm_topics_without_drafts = db.query(SuggestedTopic).filter(
    SuggestedTopic.category == "social_media",
    ~exists().where(ContentDraft.suggested_topic_id == SuggestedTopic.id)
).all()

print(f"Znaleziono {len(sm_topics_without_drafts)} tematów SM bez draftów\n")

# Create drafts for each SM topic
created_count = 0
for topic in sm_topics_without_drafts:
    # Create ContentDraft
    draft = ContentDraft(
        suggested_topic_id=topic.id,
        status="pending_generation",  # Indicates variants need to be generated
        is_active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(draft)
    db.flush()
    
    print(f"✓ Utworzono draft dla: {topic.title[:60]}...")
    created_count += 1

# Commit all changes
if created_count > 0:
    db.commit()
    print(f"\n✅ Utworzono {created_count} draftów dla tematów SM")
    print("Tematy SM powinny być teraz widoczne w pulpicie treści")
else:
    print("Nie znaleziono tematów SM do przetworzenia")

# Show current status
print("\n=== AKTUALNY STATUS ===")
total_sm_topics = db.query(SuggestedTopic).filter(
    SuggestedTopic.category == "social_media"
).count()

sm_with_drafts = db.query(SuggestedTopic).filter(
    SuggestedTopic.category == "social_media",
    exists().where(ContentDraft.suggested_topic_id == SuggestedTopic.id)
).count()

print(f"Wszystkie tematy SM: {total_sm_topics}")
print(f"Tematy SM z draftami: {sm_with_drafts}")
print(f"Pokrycie: {(sm_with_drafts/total_sm_topics*100):.1f}%" if total_sm_topics > 0 else "N/A")

db.close()