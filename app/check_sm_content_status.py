#!/usr/bin/env python3
"""Check status of SM content and why it's not showing in dashboard"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import SuggestedTopic, ContentDraft, ContentVariant, ContentPlan
from sqlalchemy import and_

db = SessionLocal()

print("=== ANALIZA STANU TREŚCI SM ===\n")

# 1. Check if there are any content plans
plans = db.query(ContentPlan).all()
print(f"Liczba planów treści: {len(plans)}")

if not plans:
    print("\n❌ Brak planów treści. Najpierw utwórz plan treści.")
    db.close()
    exit()

# 2. Check SM topics
sm_topics = db.query(SuggestedTopic).filter(
    SuggestedTopic.category == "social_media"
).all()

print(f"\nLiczba tematów SM: {len(sm_topics)}")

# 3. Check if SM topics have drafts
sm_topics_with_drafts = 0
sm_topics_without_drafts = 0

for topic in sm_topics:
    draft = db.query(ContentDraft).filter(
        ContentDraft.suggested_topic_id == topic.id
    ).first()
    
    if draft:
        sm_topics_with_drafts += 1
    else:
        sm_topics_without_drafts += 1

print(f"- Tematy SM z draftami: {sm_topics_with_drafts}")
print(f"- Tematy SM bez draftów: {sm_topics_without_drafts}")

# 4. Check blog topics for comparison
blog_topics = db.query(SuggestedTopic).filter(
    SuggestedTopic.category == "blog"
).all()

blog_topics_with_drafts = 0
for topic in blog_topics:
    draft = db.query(ContentDraft).filter(
        ContentDraft.suggested_topic_id == topic.id
    ).first()
    if draft:
        blog_topics_with_drafts += 1

print(f"\nDla porównania - wpisy blogowe:")
print(f"- Liczba tematów blog: {len(blog_topics)}")
print(f"- Tematy blog z draftami: {blog_topics_with_drafts}")

# 5. Check all drafts
all_drafts = db.query(ContentDraft).all()
print(f"\nWszystkie drafty w bazie: {len(all_drafts)}")

# 6. Show sample SM topics without drafts
if sm_topics_without_drafts > 0:
    print("\n=== PRZYKŁADOWE TEMATY SM BEZ DRAFTÓW ===")
    count = 0
    for topic in sm_topics[:5]:
        draft = db.query(ContentDraft).filter(
            ContentDraft.suggested_topic_id == topic.id
        ).first()
        
        if not draft and count < 3:
            print(f"\nID: {topic.id}")
            print(f"Tytuł: {topic.title}")
            print(f"Status: {topic.status}")
            print(f"Plan ID: {topic.content_plan_id}")
            count += 1

# 7. Solution
print("\n=== ROZWIĄZANIE ===")
print("Problem: Tematy SM nie mają utworzonych draftów (ContentDraft)")
print("Dashboard pokazuje tylko ContentDraft, więc tematy SM bez draftów są niewidoczne")
print("\nMożliwe rozwiązania:")
print("1. Automatycznie tworzyć drafty dla zatwierdzonych tematów SM")
print("2. Zmodyfikować endpoint aby pokazywał też SuggestedTopic bez draftów")
print("3. Dodać przycisk 'Generuj warianty' dla tematów SM w interfejsie")

db.close()