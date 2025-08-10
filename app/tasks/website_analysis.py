"""
Tasks for analyzing organization websites
"""

import json
import logging
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime

from celery import shared_task
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import Organization, WebsiteAnalysis
from app.core.external_integrations import TavilyIntegration

logger = logging.getLogger(__name__)


@shared_task(bind=True, name="website.analyze_organization_website")
def analyze_organization_website_task(
    self,
    organization_id: int,
    website_url: str,
    organization_name: str = None
) -> Dict[str, Any]:
    """
    Analyze organization website using Tavily API
    
    Args:
        organization_id: ID of the organization
        website_url: URL of the website to analyze
        organization_name: Optional organization name for context
        
    Returns:
        Dict with analysis results
    """
    logger.info(f"Starting website analysis for organization {organization_id}: {website_url}")
    
    db = SessionLocal()
    
    try:
        # Check if analysis already exists
        existing_analysis = db.query(WebsiteAnalysis).filter(
            WebsiteAnalysis.organization_id == organization_id
        ).first()
        
        if existing_analysis:
            # Update existing analysis
            website_analysis = existing_analysis
            website_analysis.analysis_status = 'processing'
            website_analysis.website_url = website_url
            db.commit()
        else:
            # Create new analysis record
            website_analysis = WebsiteAnalysis(
                organization_id=organization_id,
                website_url=website_url,
                analysis_status='processing'
            )
            db.add(website_analysis)
            db.commit()
        
        # Perform analysis using Tavily
        tavily = TavilyIntegration()
        
        # Run async function in sync context
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            analysis_results = loop.run_until_complete(
                tavily.analyze_website(website_url, organization_name)
            )
        finally:
            loop.close()
        
        # Check for errors
        if "error" in analysis_results:
            logger.error(f"Website analysis failed: {analysis_results['error']}")
            
            # Update with error status
            website_analysis.analysis_status = 'failed'
            website_analysis.error_message = analysis_results['error']
            website_analysis.updated_at = datetime.utcnow()
            db.commit()
            
            return {
                "status": "failed",
                "error": analysis_results['error'],
                "organization_id": organization_id
            }
        
        # Update website analysis record with results
        website_analysis.analysis_data = analysis_results
        
        # Basic fields
        website_analysis.industry_detected = analysis_results.get('industry_detected')
        website_analysis.services_detected = analysis_results.get('services_detected', [])
        website_analysis.company_values = analysis_results.get('company_values', [])
        website_analysis.target_audience = analysis_results.get('target_audience', [])
        # Content tone is managed in communication strategy, not from website analysis
        website_analysis.content_tone = None
        website_analysis.key_topics = analysis_results.get('key_topics', [])
        website_analysis.competitors_mentioned = analysis_results.get('competitors_mentioned', [])
        
        # Enhanced AI fields
        website_analysis.company_overview = analysis_results.get('company_overview')
        website_analysis.unique_selling_points = analysis_results.get('unique_selling_points', [])
        website_analysis.content_strategy_insights = analysis_results.get('content_strategy_insights')
        website_analysis.recommended_content_topics = analysis_results.get('recommended_content_topics', [])
        website_analysis.brand_personality = analysis_results.get('brand_personality')
        website_analysis.key_differentiators = analysis_results.get('key_differentiators', [])
        website_analysis.market_positioning = analysis_results.get('market_positioning')
        website_analysis.customer_pain_points = analysis_results.get('customer_pain_points', [])
        website_analysis.technology_stack = analysis_results.get('technology_stack', [])
        website_analysis.partnership_ecosystem = analysis_results.get('partnership_ecosystem', [])
        
        # Metadata
        website_analysis.last_analysis_date = datetime.utcnow()
        website_analysis.analysis_status = 'completed'
        website_analysis.error_message = None
        website_analysis.updated_at = datetime.utcnow()
        
        db.commit()
        
        # Also update organization industry if not set
        organization = db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if organization and not organization.industry and analysis_results.get('industry_detected'):
            organization.industry = analysis_results.get('industry_detected')
            db.commit()
            logger.info(f"Updated organization industry to: {organization.industry}")
        
        logger.info(f"Website analysis completed successfully for organization {organization_id}")
        
        return {
            "status": "success",
            "organization_id": organization_id,
            "website_url": website_url,
            "industry_detected": analysis_results.get('industry_detected'),
            "services_count": len(analysis_results.get('services_detected', [])),
            "topics_count": len(analysis_results.get('key_topics', [])),
            "analysis_id": website_analysis.id
        }
        
    except Exception as e:
        logger.error(f"Error in website analysis task: {str(e)}")
        
        # Update status to failed
        if 'website_analysis' in locals():
            website_analysis.analysis_status = 'failed'
            website_analysis.error_message = str(e)
            db.commit()
        
        return {
            "status": "failed",
            "error": str(e),
            "organization_id": organization_id
        }
        
    finally:
        db.close()


@shared_task(bind=True, name="website.refresh_website_analysis")
def refresh_website_analysis_task(self, organization_id: int) -> Dict[str, Any]:
    """
    Refresh website analysis for an organization
    
    Args:
        organization_id: ID of the organization
        
    Returns:
        Dict with refresh results
    """
    logger.info(f"Refreshing website analysis for organization {organization_id}")
    
    db = SessionLocal()
    
    try:
        # Get organization
        organization = db.query(Organization).filter(
            Organization.id == organization_id
        ).first()
        
        if not organization:
            return {
                "status": "failed",
                "error": "Organization not found",
                "organization_id": organization_id
            }
        
        if not organization.website:
            return {
                "status": "failed",
                "error": "Organization has no website URL",
                "organization_id": organization_id
            }
        
        # Trigger analysis
        return analyze_organization_website_task(
            organization_id=organization_id,
            website_url=organization.website,
            organization_name=organization.name
        )
        
    finally:
        db.close()


def get_website_analysis_for_organization(
    db: Session,
    organization_id: int
) -> Optional[Dict[str, Any]]:
    """
    Get website analysis data for an organization
    
    Args:
        db: Database session
        organization_id: ID of the organization
        
    Returns:
        Website analysis data or None if not found
    """
    website_analysis = db.query(WebsiteAnalysis).filter(
        WebsiteAnalysis.organization_id == organization_id,
        WebsiteAnalysis.analysis_status == 'completed'
    ).first()
    
    if not website_analysis:
        return None
    
    return {
        "industry": website_analysis.industry_detected,
        "services": website_analysis.services_detected or [],
        "values": website_analysis.company_values or [],
        "target_audience": website_analysis.target_audience or [],
        "content_tone": website_analysis.content_tone,
        "key_topics": website_analysis.key_topics or [],
        "competitors": website_analysis.competitors_mentioned or [],
        "company_overview": website_analysis.company_overview,
        "unique_selling_points": website_analysis.unique_selling_points or [],
        "brand_personality": website_analysis.brand_personality,
        "market_positioning": website_analysis.market_positioning,
        "customer_pain_points": website_analysis.customer_pain_points or [],
        "recommended_content_topics": website_analysis.recommended_content_topics or [],
        "content_strategy_insights": website_analysis.content_strategy_insights,
        "technology_stack": website_analysis.technology_stack or [],
        "full_analysis": website_analysis.analysis_data,
        "last_updated": website_analysis.last_analysis_date.isoformat() if website_analysis.last_analysis_date else None
    }