#!/usr/bin/env python3
"""Test variant generation for different topic types"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db.database import SessionLocal
from app.db.models import ContentDraft, ContentVariant, SuggestedTopic, ContentPlan
from sqlalchemy import func

db = SessionLocal()

# Get recent content plan
recent_plan = db.query(ContentPlan).order_by(ContentPlan.created_at.desc()).first()
if recent_plan:
    print(f"=== CONTENT PLAN: {recent_plan.plan_period} (ID: {recent_plan.id}) ===")
    print(f"Status: {recent_plan.status}")
    print(f"Blog posts quota: {recent_plan.blog_posts_quota}")
    print(f"SM posts quota: {recent_plan.sm_posts_quota}")
    print()
    
    # Get all topics for this plan
    topics = db.query(SuggestedTopic).filter(
        SuggestedTopic.content_plan_id == recent_plan.id
    ).all()
    
    print(f"Total topics: {len(topics)}")
    
    # Analyze by category and status
    blog_topics = [t for t in topics if t.category == "blog"]
    sm_topics = [t for t in topics if t.category == "social_media"]
    
    print(f"\nBlog topics: {len(blog_topics)}")
    print(f"SM topics: {len(sm_topics)}")
    
    # Check SM topic sources
    sm_correlated = [t for t in sm_topics if t.parent_topic_id is not None]
    sm_brief = [t for t in sm_topics if t.meta_data and t.meta_data.get("source") == "brief"]
    sm_standalone = [t for t in sm_topics if t.meta_data and t.meta_data.get("source") == "standalone"]
    
    print(f"\nSM breakdown:")
    print(f"- Blog-correlated: {len(sm_correlated)}")
    print(f"- Brief-based: {len(sm_brief)}")
    print(f"- Standalone: {len(sm_standalone)}")
    
    # Check drafts and variants
    print(f"\n=== DRAFTS AND VARIANTS ANALYSIS ===")
    
    topics_with_drafts = 0
    topics_with_variants = 0
    total_variants = 0
    
    for topic in topics:
        drafts = db.query(ContentDraft).filter(
            ContentDraft.suggested_topic_id == topic.id,
            ContentDraft.is_active == True
        ).all()
        
        if drafts:
            topics_with_drafts += 1
            
            has_variants = False
            for draft in drafts:
                variants = db.query(ContentVariant).filter(
                    ContentVariant.content_draft_id == draft.id
                ).all()
                
                if variants:
                    has_variants = True
                    total_variants += len(variants)
            
            if has_variants:
                topics_with_variants += 1
    
    print(f"Topics with drafts: {topics_with_drafts}/{len(topics)}")
    print(f"Topics with variants: {topics_with_variants}/{len(topics)}")
    print(f"Total variants: {total_variants}")
    
    # Show topics without variants
    print(f"\n=== TOPICS WITHOUT VARIANTS ===")
    for topic in topics[:10]:  # Show first 10
        drafts = db.query(ContentDraft).filter(
            ContentDraft.suggested_topic_id == topic.id,
            ContentDraft.is_active == True
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
            source = "unknown"
            if topic.parent_topic_id:
                source = "blog-correlated"
            elif topic.meta_data:
                source = topic.meta_data.get("source", "unknown")
            
            print(f"- [{topic.category}] {topic.title[:50]}... (source: {source}, status: {topic.status})")
            if drafts:
                print(f"  Has {len(drafts)} draft(s) but no variants")
            else:
                print(f"  No drafts created")

else:
    print("No content plans found")

db.close()