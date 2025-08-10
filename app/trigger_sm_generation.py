#!/usr/bin/env python3
"""Trigger SM generation for content plan"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks.main_flow import generate_correlated_sm_variants_task

# Find a content plan that has approved topics
from app.db.database import SessionLocal
from app.db.models import ContentPlan, SuggestedTopic

db = SessionLocal()

# Find content plan with approved topics
plan = db.query(ContentPlan).filter(ContentPlan.id == 6).first()
if plan:
    print(f"Found plan: {plan.plan_period}")
    
    # Check for approved topics
    approved_topics = db.query(SuggestedTopic).filter(
        SuggestedTopic.content_plan_id == plan.id,
        SuggestedTopic.status == "approved",
        SuggestedTopic.category == "blog"
    ).all()
    
    print(f"Found {len(approved_topics)} approved blog topics")
    
    if approved_topics:
        # Trigger SM generation
        result = generate_correlated_sm_variants_task.delay(plan.id)
        print(f"Triggered SM generation task: {result.id}")
    else:
        print("No approved topics found. Please approve some blog topics first.")
else:
    print("Content plan not found")

db.close()