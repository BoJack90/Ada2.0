"""
Tasks for analyzing content briefs with AI and external tools
"""

import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

from celery import shared_task
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.crud_content_brief import content_brief_crud
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService
from app.tasks.content_generation import _extract_text_from_file, _call_gemini_api
from app.db.models import ContentDraft

# Configure logging
logger = logging.getLogger(__name__)

# Try to import Tavily for research
try:
    from tavily import TavilyClient
    import os
    TAVILY_API_KEY = os.getenv('TAVILY_API_KEY')
    TAVILY_AVAILABLE = bool(TAVILY_API_KEY)
except ImportError:
    TAVILY_AVAILABLE = False
    TavilyClient = None


@shared_task(bind=True, name="content_gen.analyze_brief_task", queue='celery')
def analyze_brief_task(self, brief_id: int, file_content_b64: str, file_mime_type: str) -> Dict[str, Any]:
    """
    Analyze content brief with AI to extract key topics and insights
    
    Args:
        brief_id: ID of the content brief
        file_content_b64: Base64 encoded file content
        file_mime_type: MIME type of the file
        
    Returns:
        Dict with analysis results
    """
    logger.info(f"Starting brief analysis for brief_id: {brief_id}")
    
    try:
        # Extract text from file
        extracted_text = _extract_text_from_file(file_content_b64, file_mime_type)
        if not extracted_text:
            logger.error(f"Failed to extract text from brief file. MIME type: {file_mime_type}")
            # Use fallback for PDF content
            extracted_text = "Brief content could not be extracted. Please review the PDF manually."
        
        logger.info(f"Extracted text length: {len(extracted_text) if extracted_text else 0} characters")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Get AI prompt and model
            prompt_manager = PromptManager(db)
            ai_config = AIConfigService(db)
            
            # Create or get prompt for brief analysis
            prompt_template = prompt_manager._get_cached_prompt("analyze_content_brief")
            if not prompt_template:
                # Create default prompt if not exists
                prompt_template = """Analyze the following content brief and extract key information.

Brief Content:
{{brief_content}}

Return a valid JSON object with this exact structure (use empty arrays [] if no items found):
{{{{
  "mandatory_topics": [],
  "content_instructions": [],
  "company_news": [],
  "key_messages": [],
  "key_topics": [],
  "important_dates": [],
  "target_focus": [],
  "priority_items": [],
  "content_suggestions": [],
  "context_summary": ""
}}}}

Fill the arrays with relevant items found in the brief. If a field has no relevant content, leave it as an empty array or empty string.
DO NOT include any text outside the JSON object. Return ONLY the JSON."""
            
            model_name = ai_config._get_cached_model("analyze_content_brief")
            if not model_name:
                model_name = "models/gemini-1.5-pro-latest"
            
            # Ensure model name has correct prefix
            if model_name and not model_name.startswith("models/"):
                model_name = f"models/{model_name}"
            
            # Format prompt
            try:
                final_prompt = prompt_template.format(brief_content=extracted_text[:8000])  # Limit to 8k chars
            except KeyError as e:
                logger.error(f"KeyError in prompt formatting: {e}")
                logger.error(f"Prompt template: {prompt_template[:200]}...")
                # Use a simpler prompt
                final_prompt = f"""Analyze the following content brief and extract key information.

Brief Content:
{extracted_text[:8000]}

Return a valid JSON object with mandatory_topics, content_instructions, company_news, key_messages, key_topics, important_dates, target_focus, priority_items, content_suggestions, and context_summary."""
            
            # Log the prompt being sent
            logger.info(f"Sending prompt to AI (first 1000 chars): {final_prompt[:1000]}...")
            
            # Call AI for analysis
            ai_response = _call_gemini_api(final_prompt, model_name)
            
            if not ai_response:
                raise ValueError("AI analysis failed")
            
            # Log the raw AI response for debugging
            logger.info(f"AI raw response length: {len(ai_response)}")
            logger.info(f"AI response preview: {ai_response[:200]}...")
            
            # Parse AI response
            try:
                # Clean up the response - remove any extra whitespace or newlines
                cleaned_response = ai_response.strip()
                # Try to find JSON content if wrapped in markdown
                if "```json" in cleaned_response:
                    cleaned_response = cleaned_response.split("```json")[1].split("```")[0].strip()
                elif "```" in cleaned_response:
                    cleaned_response = cleaned_response.split("```")[1].split("```")[0].strip()
                
                analysis_data = json.loads(cleaned_response)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse AI response: {str(e)}")
                logger.error(f"Response preview: {ai_response[:500]}")
                # Fallback analysis
                analysis_data = _create_fallback_analysis(extracted_text)
            
            # Ensure all expected fields are present
            expected_fields = [
                "mandatory_topics", "content_instructions", "company_news", 
                "key_messages", "key_topics", "important_dates", "target_focus",
                "priority_items", "content_suggestions", "context_summary"
            ]
            
            for field in expected_fields:
                if field not in analysis_data:
                    if field == "context_summary":
                        analysis_data[field] = ""
                    else:
                        analysis_data[field] = []
            
            # Extract key topics (combine mandatory and regular topics for backward compatibility)
            mandatory_topics = analysis_data.get("mandatory_topics", [])
            regular_topics = analysis_data.get("key_topics", [])
            key_topics = mandatory_topics + regular_topics
            
            # Log the extracted data for debugging
            logger.info(f"Extracted mandatory topics: {mandatory_topics}")
            logger.info(f"Extracted content instructions: {analysis_data.get('content_instructions', [])}")
            logger.info(f"Extracted company news: {analysis_data.get('company_news', [])}")
            
            # Enhance with Tavily research if available
            if TAVILY_AVAILABLE and key_topics:
                enhanced_topics = _enhance_topics_with_research(key_topics[:3])  # Research top 3 topics
                analysis_data["research_insights"] = enhanced_topics
            
            # Update brief in database
            content_brief_crud.update_ai_analysis(
                db=db,
                brief_id=brief_id,
                extracted_content=extracted_text,
                key_topics=key_topics,
                ai_analysis=analysis_data
            )
            
            logger.info(f"Successfully analyzed brief {brief_id}")
            
            return {
                "status": "SUCCESS",
                "brief_id": brief_id,
                "key_topics_count": len(key_topics),
                "analysis": analysis_data
            }
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in analyze_brief_task: {str(e)}")
        self.retry(countdown=60, max_retries=3)


def _create_fallback_analysis(text: str) -> Dict[str, Any]:
    """Create basic analysis when AI fails"""
    # Simple keyword extraction
    words = text.lower().split()
    word_freq = {}
    
    for word in words:
        if len(word) > 5:  # Focus on longer words
            word_freq[word] = word_freq.get(word, 0) + 1
    
    # Get top keywords
    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    key_topics = [word[0] for word in top_words]
    
    # Look for specific patterns in text
    mandatory_topics = []
    if "tematy obowiązkowe" in text.lower() or "must cover" in text.lower():
        # Extract lines after these keywords
        lines = text.split('\n')
        for i, line in enumerate(lines):
            if "tematy obowiązkowe" in line.lower():
                # Get next 5 lines as potential topics
                for j in range(i+1, min(i+6, len(lines))):
                    if lines[j].strip():
                        mandatory_topics.append(lines[j].strip()[:100])
    
    return {
        "mandatory_topics": mandatory_topics[:5],  # Limit to 5 topics
        "content_instructions": ["Follow brief guidelines"],
        "company_news": [],
        "key_messages": ["Professional services", "Quality and safety"],
        "key_topics": key_topics,
        "important_dates": [],
        "target_focus": ["Technical directors", "Industry professionals"],
        "priority_items": ["Safety systems", "Technical compliance"],
        "content_suggestions": ["Technical guides", "Case studies", "Best practices"],
        "context_summary": f"Brief analysis based on keyword extraction. Found {len(mandatory_topics)} mandatory topics."
    }


def _enhance_topics_with_research(topics: List[str]) -> Dict[str, Any]:
    """Enhance topics with Tavily research"""
    if not TAVILY_AVAILABLE:
        return {}
    
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        research_results = {}
        
        for topic in topics:
            # Search for recent information about the topic
            response = client.search(
                query=f"{topic} trends 2024",
                search_depth="advanced",
                max_results=3
            )
            
            if response and "results" in response:
                research_results[topic] = {
                    "insights": [r.get("content", "")[:200] for r in response["results"]],
                    "sources": [r.get("url", "") for r in response["results"]]
                }
        
        return research_results
        
    except Exception as e:
        logger.error(f"Tavily research failed: {e}")
        return {}


@shared_task(bind=True, name="content_gen.generate_brief_based_content")
def generate_brief_based_content_task(self, content_plan_id: int) -> List[int]:
    """
    Generate SM content based on brief insights
    
    Args:
        content_plan_id: ID of the content plan
        
    Returns:
        List of generated topic IDs
    """
    logger.info(f"Generating brief-based content for plan {content_plan_id}")
    
    try:
        db = SessionLocal()
        
        try:
            # Get briefs for the content plan
            briefs = content_brief_crud.get_by_content_plan(db, content_plan_id)
            if not briefs:
                logger.warning(f"No briefs found for plan {content_plan_id}")
                return []
            
            # Get correlation rules
            from app.db.crud_content_brief import correlation_rule_crud
            rules = correlation_rule_crud.get_by_content_plan(db, content_plan_id)
            
            if not rules or rules.brief_based_sm_posts == 0:
                logger.info("No brief-based SM posts configured")
                return []
            
            # Combine brief insights - include ALL information
            combined_context = {
                "key_topics": [],
                "priority_items": [],
                "content_suggestions": [],
                "company_news": [],
                "content_instructions": [],
                "brief_excerpts": []
            }
            
            for brief in briefs:
                if brief.ai_analysis:
                    analysis = brief.ai_analysis
                    combined_context["key_topics"].extend(analysis.get("key_topics", []))
                    combined_context["priority_items"].extend(analysis.get("priority_items", []))
                    combined_context["content_suggestions"].extend(analysis.get("content_suggestions", []))
                    combined_context["company_news"].extend(analysis.get("company_news", []))
                    combined_context["content_instructions"].extend(analysis.get("content_instructions", []))
                
                # Also include direct brief content for better context
                if brief.extracted_content:
                    # Extract key sections about new employees or company news
                    if "Dołączyła do nas" in brief.extracted_content or "Dołączył do nas" in brief.extracted_content:
                        start = max(0, brief.extracted_content.find("Dołączył") - 10)
                        end = min(len(brief.extracted_content), start + 500)
                        combined_context["brief_excerpts"].append(brief.extracted_content[start:end])
            
            # Generate topics based on brief insights
            generated_topic_ids = []
            
            # Get AI prompt for brief-based generation
            prompt_manager = PromptManager(db)
            ai_config = AIConfigService(db)
            
            prompt_template = prompt_manager._get_cached_prompt("generate_sm_from_brief")
            if not prompt_template:
                prompt_template = """Based on the following brief insights, generate {count} social media post ideas:

Brief Context:
- Key Topics: {key_topics}
- Priority Items: {priority_items}
- Content Suggestions: {content_suggestions}

Generate engaging social media posts that address these topics and priorities.
Return as JSON array with objects containing "title" and "description"."""
            
            model_name = ai_config._get_cached_model("generate_sm_from_brief") or "gemini-1.5-pro-latest"
            
            # Format prompt with all available context
            final_prompt = prompt_template.format(
                count=rules.brief_based_sm_posts,
                key_topics=", ".join(combined_context["key_topics"][:10]) if combined_context["key_topics"] else "brak",
                priority_items=", ".join(combined_context["priority_items"][:5]) if combined_context["priority_items"] else "brak",
                content_suggestions=", ".join(combined_context["content_suggestions"][:5]) if combined_context["content_suggestions"] else "brak",
                company_news="\n".join(combined_context["company_news"][:10]) if combined_context["company_news"] else "brak",
                brief_excerpts="\n".join(combined_context["brief_excerpts"][:3]) if combined_context["brief_excerpts"] else ""
            )
            
            # Generate with AI
            ai_response = _call_gemini_api(final_prompt, model_name)
            
            if ai_response:
                try:
                    topics_data = json.loads(ai_response)
                    
                    # Save generated topics
                    from app.db import models
                    
                    for topic_data in topics_data:
                        if isinstance(topic_data, dict) and "title" in topic_data:
                            topic = models.SuggestedTopic(
                                title=topic_data["title"],
                                description=topic_data.get("description", ""),
                                category="social_media",
                                content_plan_id=content_plan_id,
                                status="approved",  # Auto-approve brief-based content
                                meta_data={"source": "brief", "brief_based": True},
                                is_active=True,
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            db.add(topic)
                            db.flush()
                            generated_topic_ids.append(topic.id)
                            
                            # Don't create draft here - variant generation task will create it
                            # This avoids duplicate drafts
                    
                    db.commit()
                    logger.info(f"Generated {len(generated_topic_ids)} brief-based topics")
                    
                except (json.JSONDecodeError, Exception) as e:
                    logger.error(f"Error processing AI response: {e}")
            
            return generated_topic_ids
            
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"Error in generate_brief_based_content_task: {str(e)}")
        return []