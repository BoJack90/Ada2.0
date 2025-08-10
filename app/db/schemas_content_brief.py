"""
Pydantic schemas for content briefs and correlation rules
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# Content Brief Schemas
class ContentBriefBase(BaseModel):
    title: str = Field(..., max_length=200)
    description: Optional[str] = None
    priority_level: int = Field(default=5, ge=1, le=10)


class ContentBriefCreate(ContentBriefBase):
    content_plan_id: int
    file_content: Optional[str] = None  # Base64 encoded file content
    file_type: Optional[str] = None


class ContentBriefUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority_level: Optional[int] = Field(None, ge=1, le=10)


class ContentBrief(ContentBriefBase):
    id: int
    content_plan_id: int
    file_path: Optional[str]
    file_type: Optional[str]
    extracted_content: Optional[str]
    key_topics: Optional[List[str]]
    ai_analysis: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Correlation Rule Schemas
class CorrelationRuleBase(BaseModel):
    rule_type: str = Field(..., pattern="^(blog_to_sm|brief_to_sm|standalone)$")
    sm_posts_per_blog: int = Field(default=2, ge=0, le=10)
    brief_based_sm_posts: int = Field(default=0, ge=0)
    standalone_sm_posts: int = Field(default=0, ge=0)
    platform_rules: Optional[Dict[str, int]] = None
    correlation_strength: str = Field(default="moderate", pattern="^(tight|moderate|loose)$")
    timing_strategy: str = Field(default="distributed", pattern="^(distributed|clustered|sequential)$")


class CorrelationRuleCreate(CorrelationRuleBase):
    content_plan_id: int


class CorrelationRuleUpdate(BaseModel):
    rule_type: Optional[str] = None
    sm_posts_per_blog: Optional[int] = Field(None, ge=0, le=10)
    brief_based_sm_posts: Optional[int] = Field(None, ge=0)
    standalone_sm_posts: Optional[int] = Field(None, ge=0)
    platform_rules: Optional[Dict[str, int]] = None
    correlation_strength: Optional[str] = None
    timing_strategy: Optional[str] = None


class CorrelationRule(CorrelationRuleBase):
    id: int
    content_plan_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Platform distribution schema for UI
class PlatformDistribution(BaseModel):
    platform: str
    posts_count: int
    correlation_type: str  # blog_correlated, brief_correlated, standalone