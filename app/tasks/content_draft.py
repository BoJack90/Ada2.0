"""
Content Draft generation tasks using Celery.
Implements the flexible generate_draft_task with different revision modes and author-reviewer loop.
"""

import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from celery import shared_task
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db import crud, models, schemas
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService
from app.tasks.content_generation import _call_gemini_api  # Reuse existing Gemini integration

# Configure logging
logger = logging.getLogger(__name__)


@shared_task(bind=True, name="content_draft.generate_draft_task")
def generate_draft_task(
    self, 
    scheduled_post_id: int, 
    revision_mode: Optional[str] = None, 
    revision_context: Optional[dict] = None
) -> Dict[str, Any]:
    """
    Flexible task for generating content drafts with different modes.
    
    Args:
        scheduled_post_id: ID of the scheduled post to generate draft for
        revision_mode: 'feedback', 'regenerate' or None (initial draft)
        revision_context: Additional context for revisions (feedback, previous content, etc.)
        
    Returns:
        Dict with task results and generated draft info
    """
    logger.info(f"Starting generate_draft_task for post_id: {scheduled_post_id}, mode: {revision_mode}")
    
    try:
        # Create database session
        db = SessionLocal()
        
        try:
            # Get scheduled post and related data
            scheduled_post = db.query(models.ScheduledPost).filter(
                models.ScheduledPost.id == scheduled_post_id
            ).first()
            
            if not scheduled_post:
                raise ValueError(f"ScheduledPost with ID {scheduled_post_id} not found")
            
            # Get content plan
            content_plan = crud.content_plan_crud.get_by_id(db, scheduled_post.content_plan_id)
            if not content_plan:
                raise ValueError(f"ContentPlan not found for post {scheduled_post_id}")
            
            # Get organization and strategy context
            context_data = _build_content_context(db, content_plan.organization_id, scheduled_post)
            
            # Determine prompt based on revision mode
            prompt_name = _get_prompt_name_for_mode(revision_mode)
            
            # Get AI prompt and model
            prompt_manager = PromptManager(db)
            ai_config = AIConfigService(db)
            
            prompt_template = prompt_manager._get_cached_prompt(prompt_name)
            model_name = ai_config._get_cached_model(prompt_name)
            
            if not prompt_template:
                raise ValueError(f"AI prompt '{prompt_name}' not found")
            
            if not model_name:
                raise ValueError(f"AI model assignment '{prompt_name}' not found")
            
            logger.info(f"Using prompt: {prompt_name}, model: {model_name}")
            
            # Format prompt based on revision mode
            formatted_prompt = _format_prompt_for_mode(
                prompt_template, 
                context_data, 
                scheduled_post, 
                revision_mode, 
                revision_context
            )
            
            logger.info("Calling Gemini API for content generation with Author-Reviewer loop")
            
            # Implement Author-Reviewer loop
            final_content = _author_reviewer_loop(formatted_prompt, model_name)
            
            if not final_content:
                raise ValueError("Failed to generate content using Author-Reviewer loop")
            
            # Create content draft
            draft_create = schemas.ContentDraftCreate(
                scheduled_post_id=scheduled_post_id,
                content_text=final_content,
                status='pending_approval',
                created_by_task_id=self.request.id
            )
            
            created_draft = crud.content_draft_crud.create(db, draft_create)
            logger.info(f"Created ContentDraft ID: {created_draft.id}, version: {created_draft.version}")
            
            # Create revision record if this is a revision
            if revision_mode and revision_context:
                revision_create = schemas.DraftRevisionCreate(
                    content_draft_id=created_draft.id,
                    revision_type=revision_mode,
                    feedback_text=revision_context.get('feedback_text'),
                    previous_content=revision_context.get('previous_content'),
                    revision_context=json.dumps(revision_context),
                    created_by_user_id=revision_context.get('user_id'),
                    task_id=self.request.id
                )
                
                crud.draft_revision_crud.create(db, revision_create)
                logger.info(f"Created DraftRevision for draft {created_draft.id}")
            
            return {
                "status": "SUCCESS",
                "draft_id": created_draft.id,
                "scheduled_post_id": scheduled_post_id,
                "version": created_draft.version,
                "revision_mode": revision_mode,
                "content_length": len(final_content),
                "message": f"Successfully generated draft version {created_draft.version}"
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in generate_draft_task: {str(e)}")
        self.retry(countdown=120, max_retries=2)


def _get_prompt_name_for_mode(revision_mode: Optional[str]) -> str:
    """Get appropriate prompt name based on revision mode."""
    if revision_mode == 'feedback':
        return 'revise_draft_with_feedback'
    elif revision_mode == 'regenerate':
        return 'regenerate_draft_from_rejection'
    else:
        return 'generate_initial_draft'


def _build_content_context(db: Session, organization_id: int, scheduled_post: models.ScheduledPost) -> Dict[str, Any]:
    """
    Build comprehensive context for content generation.
    Similar to contextualize_task but focused on single post.
    """
    # Get organization
    organization = crud.organization_crud.get_by_id(db, organization_id)
    
    # Get website analysis if available
    from app.tasks.website_analysis import get_website_analysis_for_organization
    website_analysis = get_website_analysis_for_organization(db, organization_id)
    
    # Get communication strategy
    strategies = db.query(models.CommunicationStrategy).filter(
        models.CommunicationStrategy.organization_id == organization_id,
        models.CommunicationStrategy.is_active == True
    ).order_by(models.CommunicationStrategy.created_at.desc()).limit(1).all()
    
    strategy = strategies[0] if strategies else None
    
    if strategy:
        # Get all related strategy data
        personas = db.query(models.Persona).filter(
            models.Persona.communication_strategy_id == strategy.id
        ).all()
        
        platform_styles = db.query(models.PlatformStyle).filter(
            models.PlatformStyle.communication_strategy_id == strategy.id
        ).all()
        
        cta_rules = db.query(models.CTARule).filter(
            models.CTARule.communication_strategy_id == strategy.id
        ).all()
        
        general_style = db.query(models.GeneralStyle).filter(
            models.GeneralStyle.communication_strategy_id == strategy.id
        ).first()
        
        communication_goals = db.query(models.CommunicationGoal).filter(
            models.CommunicationGoal.communication_strategy_id == strategy.id
        ).all()
        
        forbidden_phrases = db.query(models.ForbiddenPhrase).filter(
            models.ForbiddenPhrase.communication_strategy_id == strategy.id
        ).all()
        
        preferred_phrases = db.query(models.PreferredPhrase).filter(
            models.PreferredPhrase.communication_strategy_id == strategy.id
        ).all()
        
        strategy_data = {
            "strategy_name": strategy.name,
            "description": strategy.description or "",
            "communication_goals": [goal.goal_text for goal in communication_goals],
            "target_audiences": [
                {"name": persona.name, "description": persona.description} 
                for persona in personas
            ],
            "general_style": {
                "language": general_style.language if general_style else "polski",
                "tone": general_style.tone if general_style else "profesjonalny",
                "technical_content": general_style.technical_content if general_style else "dostępny",
                "employer_branding_content": general_style.employer_branding_content if general_style else "ekspercki"
            },
            "platform_styles": [
                {
                    "platform_name": ps.platform_name,
                    "length_description": ps.length_description,
                    "style_description": ps.style_description,
                    "notes": ps.notes or ""
                }
                for ps in platform_styles
            ],
            "forbidden_phrases": [fp.phrase for fp in forbidden_phrases],
            "preferred_phrases": [pp.phrase for pp in preferred_phrases],
            "cta_rules": [
                {"content_type": cta.content_type, "cta_text": cta.cta_text}
                for cta in cta_rules
            ]
        }
    else:
        # Default strategy if none found
        strategy_data = {
            "strategy_name": "Default Strategy",
            "description": "No specific communication strategy defined",
            "communication_goals": ["Increase brand awareness", "Generate engagement"],
            "target_audiences": [{"name": "General Audience", "description": "Broad target audience"}],
            "general_style": {
                "language": "polski",
                "tone": "profesjonalny",
                "technical_content": "dostępny dla wszystkich",
                "employer_branding_content": "wykazujący ekspertyze"
            },
            "platform_styles": [],
            "forbidden_phrases": [],
            "preferred_phrases": [],
            "cta_rules": []
        }
    
    return {
        "organization": {
            "name": organization.name if organization else "Unknown Organization",
            "description": organization.description if organization else "",
            "industry": website_analysis.get('industry') if website_analysis else organization.industry if organization else "",
            "website": organization.website if organization else "",
            "website_analysis": website_analysis if website_analysis else None
        },
        "communication_strategy": strategy_data
    }


def _format_prompt_for_mode(
    prompt_template: str, 
    context_data: Dict[str, Any], 
    scheduled_post: models.ScheduledPost,
    revision_mode: Optional[str], 
    revision_context: Optional[dict]
) -> str:
    """Format prompt template with appropriate data based on revision mode."""
    
    # Common data for all modes
    context_json = json.dumps(context_data, ensure_ascii=False, indent=2)
    
    post_details = {
        "publication_date": scheduled_post.publication_date.isoformat(),
        "post_type": scheduled_post.post_type or "general",
        "title": scheduled_post.title or "",
        "platform": scheduled_post.platform or "blog",
        "current_content": scheduled_post.content or ""
    }
    post_details_json = json.dumps(post_details, ensure_ascii=False, indent=2)
    
    # Base formatting
    format_data = {
        "context_data": context_json,
        "post_details": post_details_json
    }
    
    # Add revision-specific data
    if revision_mode == 'feedback' and revision_context:
        format_data.update({
            "previous_content": revision_context.get('previous_content', ''),
            "feedback_text": revision_context.get('feedback_text', ''),
            "revision_context": json.dumps(revision_context.get('additional_context', {}), ensure_ascii=False)
        })
    elif revision_mode == 'regenerate' and revision_context:
        format_data.update({
            "rejected_content": revision_context.get('previous_content', ''),
            "rejection_reason": revision_context.get('rejection_reason', 'Content did not meet quality standards'),
            "revision_context": json.dumps(revision_context.get('additional_context', {}), ensure_ascii=False)
        })
    
    return prompt_template.format(**format_data)


def _author_reviewer_loop(prompt: str, model_name: str, max_iterations: int = 3) -> str:
    """
    Implement Author-Reviewer loop for high-quality content generation.
    
    Args:
        prompt: Formatted prompt for content generation
        model_name: AI model to use
        max_iterations: Maximum number of author-reviewer iterations
        
    Returns:
        Final optimized content
    """
    logger.info(f"Starting Author-Reviewer loop with max {max_iterations} iterations")
    
    # Step 1: Initial content generation (Author)
    author_prompt = f"""
    {prompt}
    
    AUTHOR ROLE: Generate the initial content draft following all guidelines.
    """
    
    initial_content = _call_gemini_api(author_prompt, model_name)
    if not initial_content:
        logger.error("Failed to generate initial content")
        return ""
    
    current_content = initial_content.strip()
    logger.info(f"Author generated initial content ({len(current_content)} chars)")
    
    # Step 2: Iterative review and improvement
    for iteration in range(max_iterations):
        logger.info(f"Author-Reviewer iteration {iteration + 1}/{max_iterations}")
        
        # Reviewer phase
        reviewer_prompt = f"""
        REVIEWER ROLE: You are reviewing content for quality and effectiveness.
        
        CONTENT TO REVIEW:
        {current_content}
        
        ORIGINAL REQUIREMENTS:
        {prompt}
        
        Analyze this content and provide specific improvement suggestions focusing on:
        1. Alignment with communication strategy
        2. Engagement and readability
        3. Call-to-action effectiveness
        4. Platform-specific optimization
        5. Overall quality and impact
        
        Provide constructive feedback for improvements or respond "APPROVED" if content is excellent.
        """
        
        review_feedback = _call_gemini_api(reviewer_prompt, model_name)
        if not review_feedback:
            logger.warning(f"No reviewer feedback received at iteration {iteration + 1}")
            break
        
        # Check if content is approved
        if "APPROVED" in review_feedback.upper():
            logger.info(f"Content approved by reviewer at iteration {iteration + 1}")
            break
        
        # Author improvement phase
        author_improvement_prompt = f"""
        AUTHOR ROLE: Improve the content based on reviewer feedback.
        
        CURRENT CONTENT:
        {current_content}
        
        REVIEWER FEEDBACK:
        {review_feedback}
        
        ORIGINAL REQUIREMENTS:
        {prompt}
        
        Create an improved version that addresses the reviewer's feedback while maintaining all original requirements.
        Return ONLY the improved content, no explanations.
        """
        
        improved_content = _call_gemini_api(author_improvement_prompt, model_name)
        if improved_content and improved_content.strip():
            current_content = improved_content.strip()
            logger.info(f"Author improved content at iteration {iteration + 1} ({len(current_content)} chars)")
        else:
            logger.warning(f"Failed to improve content at iteration {iteration + 1}")
            break
    
    logger.info(f"Author-Reviewer loop completed. Final content: {len(current_content)} chars")
    return current_content 