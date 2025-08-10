"""
Advanced Content Generation API Endpoints

Provides endpoints for the new deep reasoning content generation system.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from celery import chain

from app.db.database import get_db
from app.core.dependencies import get_current_user
from app.db import crud, models, schemas
from app.tasks.advanced_content_generation import (
    advanced_contextualize_task,
    generate_topics_with_reasoning_task,
    generate_smart_content_variants_task
)
from app.core.external_integrations import (
    TavilyIntegration,
    ContentResearchOrchestrator
)

router = APIRouter(
    prefix="/api/v1/advanced",
    tags=["Advanced Content Generation"]
)


@router.post("/content-plans/{plan_id}/generate-with-reasoning")
async def generate_content_with_reasoning(
    plan_id: int,
    background_tasks: BackgroundTasks,
    force_regenerate: bool = Query(False, description="Force regenerate even if topics exist"),
    use_deep_research: bool = Query(True, description="Use deep research with external sources"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate content topics using advanced deep reasoning system
    
    This endpoint:
    1. Performs deep context analysis including brief understanding
    2. Conducts industry research using Tavily and other sources
    3. Uses multi-step reasoning to generate highly relevant topics
    4. Ensures brief alignment and content diversity
    """
    # Get content plan
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    # Check organization access
    if not crud.organization_crud.user_has_access(
        db, current_user.id, content_plan.organization_id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if topics already exist
    existing_topics = db.query(models.SuggestedTopic).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.SuggestedTopic.is_active == True
    ).count()
    
    if existing_topics > 0 and not force_regenerate:
        return {
            "message": "Topics already exist. Use force_regenerate=true to regenerate.",
            "existing_topics": existing_topics,
            "plan_id": plan_id
        }
    
    # Deactivate existing topics if force regenerate
    if force_regenerate and existing_topics > 0:
        db.query(models.SuggestedTopic).filter(
            models.SuggestedTopic.content_plan_id == plan_id
        ).update({"is_active": False})
        db.commit()
    
    # Create task chain for advanced generation
    task_chain = chain(
        advanced_contextualize_task.s(plan_id),
        generate_topics_with_reasoning_task.s(plan_id)
    )
    
    # Execute task chain
    result = task_chain.apply_async()
    
    # Update content plan status
    content_plan.status = 'generating_topics'
    content_plan.meta_data = content_plan.meta_data or {}
    content_plan.meta_data['generation_method'] = 'deep_reasoning'
    content_plan.meta_data['use_deep_research'] = use_deep_research
    content_plan.meta_data['task_id'] = result.id
    db.commit()
    
    return {
        "message": "Advanced topic generation started",
        "task_id": result.id,
        "plan_id": plan_id,
        "generation_method": "deep_reasoning",
        "expected_topics": content_plan.blog_posts_quota + 3
    }


@router.get("/content-plans/{plan_id}/generation-insights")
async def get_generation_insights(
    plan_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get insights from the content generation process
    
    Returns detailed information about:
    - Brief analysis results
    - Industry insights used
    - Topic diversity metrics
    - Reasoning steps taken
    """
    # Get content plan
    content_plan = crud.content_plan_crud.get_by_id(db, plan_id)
    if not content_plan:
        raise HTTPException(status_code=404, detail="Content plan not found")
    
    # Check access
    if not crud.organization_crud.user_has_access(
        db, current_user.id, content_plan.organization_id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get generated topics with metadata
    topics = db.query(models.SuggestedTopic).filter(
        models.SuggestedTopic.content_plan_id == plan_id,
        models.SuggestedTopic.is_active == True
    ).all()
    
    # Extract insights from topic metadata
    insights = {
        "total_topics": len(topics),
        "topic_distribution": {},
        "brief_alignment_scores": [],
        "priority_scores": [],
        "content_types": {},
        "reasoning_available": False
    }
    
    for topic in topics:
        meta_data = topic.meta_data or {}
        
        # Content type distribution
        content_type = meta_data.get("content_type", "unknown")
        insights["content_types"][content_type] = insights["content_types"].get(content_type, 0) + 1
        
        # Topic pillar distribution
        pillar = meta_data.get("pillar", "general")
        insights["topic_distribution"][pillar] = insights["topic_distribution"].get(pillar, 0) + 1
        
        # Scores
        if "priority_score" in meta_data:
            insights["priority_scores"].append(meta_data["priority_score"])
        
        if "brief_alignment" in meta_data:
            insights["brief_alignment_scores"].append(len(meta_data["brief_alignment"]))
        
        if "reasoning_steps" in meta_data:
            insights["reasoning_available"] = True
    
    # Calculate averages
    if insights["priority_scores"]:
        insights["avg_priority_score"] = sum(insights["priority_scores"]) / len(insights["priority_scores"])
    
    if insights["brief_alignment_scores"]:
        insights["avg_brief_alignment"] = sum(insights["brief_alignment_scores"]) / len(insights["brief_alignment_scores"])
    
    # Get brief insights
    from app.db.crud_content_brief import content_brief_crud
    briefs = content_brief_crud.get_by_content_plan(db, plan_id)
    
    insights["brief_analysis"] = {
        "total_briefs": len(briefs),
        "analyzed_briefs": sum(1 for b in briefs if b.ai_analysis),
        "key_topics_extracted": []
    }
    
    for brief in briefs:
        if brief.ai_analysis:
            insights["brief_analysis"]["key_topics_extracted"].extend(
                brief.ai_analysis.get("key_topics", [])[:5]
            )
    
    # Deduplicate key topics
    insights["brief_analysis"]["key_topics_extracted"] = list(
        set(insights["brief_analysis"]["key_topics_extracted"])
    )[:20]
    
    return insights


@router.post("/research/topic")
async def research_topic(
    request: schemas.ResearchRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Perform deep research on a specific topic
    
    Uses Tavily and other sources to gather comprehensive insights
    about a topic before content generation.
    """
    # Validate organization access
    if request.organization_id:
        if not crud.organization_crud.user_has_access(
            db, current_user.id, request.organization_id
        ):
            raise HTTPException(status_code=403, detail="Access denied")
        
        organization = crud.organization_crud.get_by_id(db, request.organization_id)
        org_context = {
            "name": organization.name,
            "industry": organization.industry or "business",
            "website": organization.website
        }
    else:
        org_context = {
            "name": "Unknown",
            "industry": request.industry or "business"
        }
    
    # Initialize research orchestrator
    orchestrator = ContentResearchOrchestrator()
    
    # Perform research
    research_results = await orchestrator.comprehensive_research(
        topic=request.topic,
        organization_context=org_context,
        research_depth=request.depth or "deep"
    )
    
    # Store research results in database if organization provided
    if request.organization_id and request.store_results:
        research_record = models.ResearchResult(
            organization_id=request.organization_id,
            topic=request.topic,
            research_data=research_results,
            created_by_id=current_user.id
        )
        db.add(research_record)
        db.commit()
        
        research_results["stored_id"] = research_record.id
    
    return {
        "topic": request.topic,
        "research_completed": True,
        "sources_used": list(research_results.get("sources", {}).keys()),
        "synthesis": research_results.get("synthesis", {}),
        "full_results": research_results if request.include_raw_data else None
    }


@router.post("/topics/{topic_id}/generate-smart-variant")
async def generate_smart_variant(
    topic_id: int,
    platform_name: str,
    regenerate: bool = Query(False, description="Regenerate even if variant exists"),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Generate a smart content variant for a specific platform
    
    Uses context-aware generation with:
    - Brief alignment
    - Platform optimization
    - SEO considerations
    - Brand voice consistency
    """
    # Get topic
    topic = db.query(models.SuggestedTopic).filter(
        models.SuggestedTopic.id == topic_id,
        models.SuggestedTopic.is_active == True
    ).first()
    
    if not topic:
        raise HTTPException(status_code=404, detail="Topic not found")
    
    # Check access via content plan
    content_plan = crud.content_plan_crud.get_by_id(db, topic.content_plan_id)
    if not crud.organization_crud.user_has_access(
        db, current_user.id, content_plan.organization_id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Check if variant already exists
    existing_draft = db.query(models.ContentDraft).filter(
        models.ContentDraft.suggested_topic_id == topic_id,
        models.ContentDraft.is_active == True
    ).first()
    
    if existing_draft and not regenerate:
        existing_variant = db.query(models.ContentVariant).filter(
            models.ContentVariant.content_draft_id == existing_draft.id,
            models.ContentVariant.platform_name == platform_name,
            models.ContentVariant.is_active == True
        ).first()
        
        if existing_variant:
            return {
                "message": "Variant already exists",
                "variant_id": existing_variant.id,
                "platform": platform_name
            }
    
    # Generate smart variant
    result = generate_smart_content_variants_task.delay(
        topic_id=topic_id,
        platform_name=platform_name
    )
    
    return {
        "message": "Smart variant generation started",
        "task_id": result.id,
        "topic_id": topic_id,
        "platform": platform_name
    }


@router.get("/analytics/content-performance")
async def get_content_performance_analytics(
    organization_id: int,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    """
    Get analytics on content generation performance
    
    Provides insights on:
    - Topic approval rates
    - Brief alignment success
    - Content diversity metrics
    - Generation method comparison
    """
    # Check access
    if not crud.organization_crud.user_has_access(
        db, current_user.id, organization_id
    ):
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Build date filters
    date_filters = []
    if date_from:
        date_filters.append(models.ContentPlan.created_at >= date_from)
    if date_to:
        date_filters.append(models.ContentPlan.created_at <= date_to)
    
    # Get content plans
    plans = db.query(models.ContentPlan).filter(
        models.ContentPlan.organization_id == organization_id,
        *date_filters
    ).all()
    
    analytics = {
        "total_plans": len(plans),
        "topic_metrics": {
            "total_generated": 0,
            "total_approved": 0,
            "total_rejected": 0,
            "approval_rate": 0
        },
        "generation_methods": {
            "standard": 0,
            "deep_reasoning": 0
        },
        "content_diversity": {
            "avg_priority_score": 0,
            "content_type_distribution": {},
            "pillar_distribution": {}
        },
        "brief_utilization": {
            "plans_with_briefs": 0,
            "avg_briefs_per_plan": 0,
            "brief_alignment_rate": 0
        }
    }
    
    # Aggregate metrics
    total_priority_scores = []
    brief_counts = []
    
    for plan in plans:
        # Count generation method
        if plan.meta_data and plan.meta_data.get("generation_method") == "deep_reasoning":
            analytics["generation_methods"]["deep_reasoning"] += 1
        else:
            analytics["generation_methods"]["standard"] += 1
        
        # Get topics for this plan
        topics = db.query(models.SuggestedTopic).filter(
            models.SuggestedTopic.content_plan_id == plan.id,
            models.SuggestedTopic.is_active == True
        ).all()
        
        analytics["topic_metrics"]["total_generated"] += len(topics)
        
        # Count statuses
        for topic in topics:
            if topic.status == "approved":
                analytics["topic_metrics"]["total_approved"] += 1
            elif topic.status == "rejected":
                analytics["topic_metrics"]["total_rejected"] += 1
            
            # Extract metrics from metadata
            if topic.meta_data:
                priority = topic.meta_data.get("priority_score")
                if priority:
                    total_priority_scores.append(priority)
                
                content_type = topic.meta_data.get("content_type", "unknown")
                analytics["content_diversity"]["content_type_distribution"][content_type] = \
                    analytics["content_diversity"]["content_type_distribution"].get(content_type, 0) + 1
                
                pillar = topic.meta_data.get("pillar", "general")
                analytics["content_diversity"]["pillar_distribution"][pillar] = \
                    analytics["content_diversity"]["pillar_distribution"].get(pillar, 0) + 1
        
        # Count briefs
        from app.db.crud_content_brief import content_brief_crud
        brief_count = content_brief_crud.count_by_content_plan(db, plan.id)
        if brief_count > 0:
            analytics["brief_utilization"]["plans_with_briefs"] += 1
            brief_counts.append(brief_count)
    
    # Calculate rates and averages
    if analytics["topic_metrics"]["total_generated"] > 0:
        analytics["topic_metrics"]["approval_rate"] = (
            analytics["topic_metrics"]["total_approved"] / 
            analytics["topic_metrics"]["total_generated"]
        ) * 100
    
    if total_priority_scores:
        analytics["content_diversity"]["avg_priority_score"] = (
            sum(total_priority_scores) / len(total_priority_scores)
        )
    
    if brief_counts:
        analytics["brief_utilization"]["avg_briefs_per_plan"] = (
            sum(brief_counts) / len(brief_counts)
        )
    
    if analytics["brief_utilization"]["plans_with_briefs"] > 0:
        analytics["brief_utilization"]["brief_alignment_rate"] = (
            analytics["brief_utilization"]["plans_with_briefs"] / 
            analytics["total_plans"]
        ) * 100
    
    return analytics


# Add Pydantic schemas
from pydantic import BaseModel, Field

class ResearchRequest(BaseModel):
    topic: str = Field(..., description="Topic to research")
    organization_id: Optional[int] = Field(None, description="Organization ID for context")
    industry: Optional[str] = Field(None, description="Industry if organization not provided")
    depth: Optional[str] = Field("deep", description="Research depth: basic, deep, comprehensive")
    include_raw_data: bool = Field(False, description="Include raw research data in response")
    store_results: bool = Field(True, description="Store research results in database")

# Update schemas module
schemas.ResearchRequest = ResearchRequest