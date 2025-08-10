#!/usr/bin/env python3
"""Trigger topic generation for content plan"""
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.tasks.main_flow import contextualize_task, generate_and_save_blog_topics_task
from celery import chain

# Content plan ID
plan_id = 6

# Build and execute the task chain
task_chain = chain(
    contextualize_task.s(plan_id),
    generate_and_save_blog_topics_task.s(plan_id)
)

# Execute the chain
result = task_chain.apply_async()

print(f"Triggered topic generation task chain: {result.id}")
print(f"First task ID: {result.parent.id if result.parent else 'N/A'}")