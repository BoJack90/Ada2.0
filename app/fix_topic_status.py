#!/usr/bin/env python3
"""Fix topic status to enable variant generation"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic, ContentPlan
from datetime import datetime

db = SessionLocal()

# Get recent content plan
recent_plan = db.query(ContentPlan).order_by(ContentPlan.created_at.desc()).first()

if recent_plan:
    print(f"=== FIXING TOPICS FOR PLAN: {recent_plan.plan_period} (ID: {recent_plan.id}) ===")
    
    # Get all topics with "suggested" status
    suggested_topics = db.query(SuggestedTopic).filter(
        SuggestedTopic.content_plan_id == recent_plan.id,
        SuggestedTopic.status == "suggested"
    ).all()
    
    print(f"Found {len(suggested_topics)} topics with 'suggested' status")
    
    # Update them to approved
    for topic in suggested_topics:
        print(f"Updating: [{topic.category}] {topic.title[:50]}...")
        topic.status = "approved"
        topic.updated_at = datetime.utcnow()
    
    db.commit()
    print(f"\nUpdated {len(suggested_topics)} topics to 'approved' status")
    
    # Now trigger variant generation for topics without variants
    from app.tasks.variant_generation import generate_all_variants_for_topic_task
    
    all_topics = db.query(SuggestedTopic).filter(
        SuggestedTopic.content_plan_id == recent_plan.id,
        SuggestedTopic.status == "approved"
    ).all()
    
    print(f"\n=== TRIGGERING VARIANT GENERATION ===")
    tasks_triggered = 0
    
    for topic in all_topics:
        # Check if topic has variants
        from app.db.models import ContentDraft, ContentVariant
        
        drafts = db.query(ContentDraft).filter(
            ContentDraft.suggested_topic_id == topic.id
        ).all()
        
        has_variants = False
        for draft in drafts:
            variants = db.query(ContentVariant).filter(
                ContentVariant.content_draft_id == draft.id
            ).all()
            if variants:
                has_variants = True
                break
        
        if not has_variants:
            print(f"Triggering generation for: {topic.title[:50]}...")
            try:
                result = generate_all_variants_for_topic_task.delay(topic.id)
                print(f"  Task ID: {result.id}")
                tasks_triggered += 1
            except Exception as e:
                print(f"  Error: {e}")
    
    print(f"\nTriggered {tasks_triggered} variant generation tasks")

else:
    print("No content plans found")

db.close()