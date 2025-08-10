from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


# Persona Schemas
class PersonaBase(BaseModel):
    name: str
    description: str

class PersonaCreate(PersonaBase):
    pass

class PersonaUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

class Persona(PersonaBase):
    id: int
    communication_strategy_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Platform Style Schemas  
class PlatformStyleBase(BaseModel):
    platform_name: str
    length_description: str
    style_description: str
    notes: Optional[str] = None

class PlatformStyleCreate(PlatformStyleBase):
    pass

class PlatformStyleUpdate(BaseModel):
    platform_name: Optional[str] = None
    length_description: Optional[str] = None
    style_description: Optional[str] = None
    notes: Optional[str] = None

class PlatformStyle(PlatformStyleBase):
    id: int
    communication_strategy_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# CTA Rule Schemas
class CTARuleBase(BaseModel):
    content_type: str
    cta_text: str

class CTARuleCreate(CTARuleBase):
    pass

class CTARuleUpdate(BaseModel):
    content_type: Optional[str] = None
    cta_text: Optional[str] = None

class CTARule(CTARuleBase):
    id: int
    communication_strategy_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# General Style Schemas
class GeneralStyleBase(BaseModel):
    language: str
    tone: str
    technical_content: Optional[str] = None
    employer_branding_content: Optional[str] = None

class GeneralStyleCreate(GeneralStyleBase):
    pass

class GeneralStyleUpdate(BaseModel):
    language: Optional[str] = None
    tone: Optional[str] = None
    technical_content: Optional[str] = None
    employer_branding_content: Optional[str] = None

class GeneralStyle(GeneralStyleBase):
    id: int
    communication_strategy_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Communication Strategy Schemas (Complete Schema as per user's request)
class CommunicationStrategyBase(BaseModel):
    name: str
    description: Optional[str] = None

class CommunicationStrategyCreate(CommunicationStrategyBase):
    organization_id: int
    communication_goals: List[str] = []
    target_audiences: List[PersonaCreate] = []
    general_style: Optional[GeneralStyleCreate] = None
    platform_styles: List[PlatformStyleCreate] = []
    forbidden_phrases: List[str] = []
    preferred_phrases: List[str] = []
    cta_rules: List[CTARuleCreate] = []
    sample_content_types: List[str] = []

class CommunicationStrategyUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    communication_goals: Optional[List[str]] = None
    target_audiences: Optional[List[PersonaUpdate]] = None
    general_style: Optional[GeneralStyleUpdate] = None
    platform_styles: Optional[List[PlatformStyleUpdate]] = None
    forbidden_phrases: Optional[List[str]] = None
    preferred_phrases: Optional[List[str]] = None
    cta_rules: Optional[List[CTARuleUpdate]] = None
    sample_content_types: Optional[List[str]] = None

class CommunicationStrategy(CommunicationStrategyBase):
    id: int
    organization_id: int
    created_by_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Related data
    communication_goals: List[str] = []
    target_audiences: List[Persona] = []
    general_style: Optional[GeneralStyle] = None
    platform_styles: List[PlatformStyle] = []
    forbidden_phrases: List[str] = []
    preferred_phrases: List[str] = []
    cta_rules: List[CTARule] = []
    sample_content_types: List[str] = []
    
    class Config:
        from_attributes = True


# Suggested Topic Schemas
class SuggestedTopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None

class SuggestedTopicCreate(SuggestedTopicBase):
    organization_id: int

class SuggestedTopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class SuggestedTopic(SuggestedTopicBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Topic Status Update Schema
class TopicStatusUpdate(BaseModel):
    status: str  # approved, rejected, suggested

# Content Plan Schemas
class ContentPlanBase(BaseModel):
    plan_period: str
    blog_posts_quota: int
    sm_posts_quota: int
    correlate_posts: bool = True
    scheduling_mode: str = 'auto'
    scheduling_preferences: Optional[str] = None

class ContentPlanCreate(ContentPlanBase):
    organization_id: int

class ContentPlanUpdate(BaseModel):
    plan_period: Optional[str] = None
    blog_posts_quota: Optional[int] = None
    sm_posts_quota: Optional[int] = None
    correlate_posts: Optional[bool] = None
    scheduling_mode: Optional[str] = None
    scheduling_preferences: Optional[str] = None
    is_active: Optional[bool] = None

class ContentPlan(ContentPlanBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Scheduled Post Schemas
class ScheduledPostBase(BaseModel):
    publication_date: datetime
    status: str = 'scheduled'
    post_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    platform: Optional[str] = None

class ScheduledPostCreate(ScheduledPostBase):
    content_plan_id: int
    suggested_topic_id: Optional[int] = None

class ScheduledPostUpdate(BaseModel):
    publication_date: Optional[datetime] = None
    status: Optional[str] = None
    post_type: Optional[str] = None
    title: Optional[str] = None
    content: Optional[str] = None
    platform: Optional[str] = None
    suggested_topic_id: Optional[int] = None

class ScheduledPost(ScheduledPostBase):
    id: int
    content_plan_id: int
    suggested_topic_id: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Content Plan with Related Data
class ContentPlanWithPosts(ContentPlan):
    scheduled_posts: List[ScheduledPost] = []
    
    class Config:
        from_attributes = True 