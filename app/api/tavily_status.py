"""
Tavily API status endpoint
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.dependencies import get_current_user, get_db
from app.core.external_integrations import TavilyIntegration
from app.db.models import User
import asyncio

router = APIRouter(prefix="/api/v1/tavily", tags=["tavily"])


@router.get("/status")
async def check_tavily_status(
    current_user: User = Depends(get_current_user)
):
    """
    Check Tavily API status and quota
    """
    tavily = TavilyIntegration()
    status = await tavily.check_tavily_status()
    
    if "error" in status:
        error_msg = status["error"]
        if "usage limit" in error_msg.lower():
            return {
                "status": "error",
                "error_type": "quota_exceeded",
                "message": "Tavily API limit exceeded. Please check your API key or upgrade your plan.",
                "details": error_msg
            }
        else:
            return {
                "status": "error",
                "error_type": "api_error",
                "message": "Tavily API error",
                "details": error_msg
            }
    
    return {
        "status": "ok",
        "message": "Tavily API is working correctly"
    }