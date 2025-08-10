#!/usr/bin/env python3
"""Test SM generation from brief"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks.brief_analysis import generate_brief_based_content_task

# Assume we have plan ID 10
plan_id = 10

print("Testing brief-based SM generation...")
print(f"Plan ID: {plan_id}")

# Call the task directly (synchronously for testing)
try:
    result = generate_brief_based_content_task(plan_id)
    print(f"\nGenerated {len(result)} SM topics from brief")
    
    if result:
        # Check the generated topics
        from app.db.database import SessionLocal
        from app.db.models import SuggestedTopic
        
        db = SessionLocal()
        
        # Get the generated topics
        topics = db.query(SuggestedTopic).filter(
            SuggestedTopic.id.in_(result)
        ).all()
        
        print("\n=== GENERATED SM TOPICS FROM BRIEF ===")
        for i, topic in enumerate(topics, 1):
            print(f"\n{i}. {topic.title}")
            print(f"   {topic.description[:150]}...")
            if topic.meta_data:
                print(f"   Meta: {topic.meta_data}")
        
        db.close()
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()