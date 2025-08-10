from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

# Enums
class TaskStatusEnum(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriorityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class UserRoleEnum(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"

# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str
    first_name: str
    last_name: str
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None

class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class OrganizationBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None

class OrganizationCreate(OrganizationBase):
    pass

class OrganizationUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    website: Optional[str] = None
    logo_url: Optional[str] = None
    industry: Optional[str] = None
    size: Optional[str] = None

class Organization(OrganizationBase):
    id: int
    is_active: bool
    owner_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationWithMembers(Organization):
    members: List[User] = []
    owner: User

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class ProjectCreate(ProjectBase):
    organization_id: int

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class Project(ProjectBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class CampaignBase(BaseModel):
    name: str
    description: Optional[str] = None
    budget: Optional[int] = None  # w groszach
    target_audience: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

class CampaignCreate(CampaignBase):
    organization_id: int
    project_id: Optional[int] = None

class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    budget: Optional[int] = None
    target_audience: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class Campaign(CampaignBase):
    id: int
    organization_id: int
    project_id: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatusEnum = TaskStatusEnum.PENDING
    priority: TaskPriorityEnum = TaskPriorityEnum.MEDIUM
    due_date: Optional[datetime] = None
    task_type: Optional[str] = None
    estimated_hours: Optional[int] = None
    tags: Optional[str] = None  # JSON string

class TaskCreate(TaskBase):
    organization_id: int
    project_id: Optional[int] = None
    campaign_id: Optional[int] = None
    assignee_id: Optional[int] = None

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatusEnum] = None
    priority: Optional[TaskPriorityEnum] = None
    due_date: Optional[datetime] = None
    assignee_id: Optional[int] = None
    task_type: Optional[str] = None
    estimated_hours: Optional[int] = None
    actual_hours: Optional[int] = None
    tags: Optional[str] = None

class Task(TaskBase):
    id: int
    organization_id: int
    project_id: Optional[int] = None
    campaign_id: Optional[int] = None
    assignee_id: Optional[int] = None
    created_by_id: int
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    actual_hours: Optional[int] = None
    
    class Config:
        from_attributes = True

class TaskWithDetails(Task):
    assignee: Optional[User] = None
    creator: User
    organization: Organization
    project: Optional[Project] = None
    campaign: Optional[Campaign] = None

class TaskCommentBase(BaseModel):
    content: str

class TaskCommentCreate(TaskCommentBase):
    task_id: int

class TaskComment(TaskCommentBase):
    id: int
    task_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    user: User
    
    class Config:
        from_attributes = True

class TaskAttachmentBase(BaseModel):
    original_filename: str
    file_size: int
    mime_type: str

class TaskAttachment(TaskAttachmentBase):
    id: int
    task_id: int
    filename: str
    file_path: str
    uploaded_by_id: int
    created_at: datetime
    uploaded_by: User
    
    class Config:
        from_attributes = True

# Auth schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class LoginRequest(BaseModel):
    username: str  # email or username
    password: str

# Organization membership
class OrganizationMember(BaseModel):
    user: User
    role: UserRoleEnum
    joined_at: datetime
    
    class Config:
        from_attributes = True

class OrganizationInvite(BaseModel):
    email: EmailStr
    role: UserRoleEnum = UserRoleEnum.MEMBER

# Dashboard schemas
class DashboardStats(BaseModel):
    total_tasks: int
    pending_tasks: int
    in_progress_tasks: int
    completed_tasks: int
    overdue_tasks: int
    total_projects: int
    active_campaigns: int
    organization_members: int

class TasksByStatus(BaseModel):
    status: TaskStatusEnum
    count: int

class TasksByPriority(BaseModel):
    priority: TaskPriorityEnum
    count: int


# Content Generation Schemas
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


class GeneralStyleBase(BaseModel):
    language: str
    tone: str
    technical_content: str
    employer_branding_content: str

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


# Content Planning Schemas
class SuggestedTopicBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: Optional[str] = None

class SuggestedTopicCreate(SuggestedTopicBase):
    content_plan_id: int

class SuggestedTopicUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    is_active: Optional[bool] = None

class SuggestedTopic(SuggestedTopicBase):
    id: int
    content_plan_id: int
    status: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TopicStatusUpdate(BaseModel):
    status: str  # approved, rejected, suggested


class ContentPlanBase(BaseModel):
    plan_period: str
    blog_posts_quota: int
    sm_posts_quota: int
    correlate_posts: bool = True
    scheduling_mode: str = 'auto'
    scheduling_preferences: Optional[str] = None
    brief_file_path: Optional[str] = None
    status: str = 'new'
    meta_data: Optional[Dict[str, Any]] = None

class ContentPlanCreate(ContentPlanBase):
    organization_id: int = Field(..., description="ID of the organization this content plan belongs to", example=1)

class ContentPlanUpdate(BaseModel):
    plan_period: Optional[str] = None
    blog_posts_quota: Optional[int] = None
    sm_posts_quota: Optional[int] = None
    correlate_posts: Optional[bool] = None
    scheduling_mode: Optional[str] = None
    scheduling_preferences: Optional[str] = None
    brief_file_path: Optional[str] = None
    status: Optional[str] = None
    is_active: Optional[bool] = None
    meta_data: Optional[Dict[str, Any]] = None

class ContentPlan(ContentPlanBase):
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


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


class ContentPlanWithPosts(ContentPlan):
    scheduled_posts: List[ScheduledPost] = []
    
    class Config:
        from_attributes = True


# Content Draft Schemas
class ContentDraftBase(BaseModel):
    status: str = 'drafting'  # drafting, pending_approval, approved, rejected

class ContentDraftCreate(ContentDraftBase):
    suggested_topic_id: int
    created_by_task_id: Optional[str] = None

class ContentDraftUpdate(BaseModel):
    status: Optional[str] = None
    is_active: Optional[bool] = None

class ContentDraft(ContentDraftBase):
    id: int
    suggested_topic_id: int
    created_by_task_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    suggested_topic: Optional['SuggestedTopic'] = None
    variants: Optional[List['ContentVariant']] = None
    
    class Config:
        from_attributes = True


class DraftRevisionBase(BaseModel):
    revision_type: str  # feedback, regenerate, initial
    feedback_text: Optional[str] = None
    previous_content: Optional[str] = None
    revision_context: Optional[str] = None

class DraftRevisionCreate(DraftRevisionBase):
    content_draft_id: int
    created_by_user_id: Optional[int] = None
    task_id: Optional[str] = None

class DraftRevision(DraftRevisionBase):
    id: int
    content_draft_id: int
    created_by_user_id: Optional[int] = None
    task_id: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Content Draft Request/Response Schemas
class DraftStatusUpdate(BaseModel):
    status: str  # pending_approval, approved, rejected

class DraftRevisionRequest(BaseModel):
    feedback_text: str
    revision_context: Optional[dict] = None

class ContentDraftWithRevisions(ContentDraft):
    revisions: List[DraftRevision] = []
    
    class Config:
        from_attributes = True

# Content Variant Schemas
class ContentVariantBase(BaseModel):
    platform_name: str
    content_text: str
    status: str = 'pending_approval'  # pending_approval, approved, rejected, needs_revision
    version: int = 1

class ContentVariantCreate(ContentVariantBase):
    content_draft_id: int
    created_by_task_id: Optional[str] = None

class ContentVariantUpdate(BaseModel):
    content_text: Optional[str] = None
    status: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None

class ContentVariant(ContentVariantBase):
    id: int
    content_draft_id: int
    created_by_task_id: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Content Variant Request/Response Schemas
class VariantStatusUpdate(BaseModel):
    status: str  # pending_approval, approved, rejected, needs_revision

class VariantContentUpdate(BaseModel):
    content_text: str

class VariantRevisionRequest(BaseModel):
    feedback: str

class ContentDraftWithVariants(ContentDraft):
    variants: List[ContentVariant] = []
    
    class Config:
        from_attributes = True


# AI Prompt and Model Assignment schemas
class AIPromptBase(BaseModel):
    prompt_name: str
    prompt_template: str

class AIPromptCreate(AIPromptBase):
    pass

class AIPromptUpdate(BaseModel):
    prompt_template: Optional[str] = None

class AIPrompt(AIPromptBase):
    id: int
    version: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AIModelAssignmentBase(BaseModel):
    task_name: str
    model_name: str

class AIModelAssignmentCreate(AIModelAssignmentBase):
    pass

class AIModelAssignmentUpdate(BaseModel):
    model_name: Optional[str] = None

class AIModelAssignment(AIModelAssignmentBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class AIConfiguration(BaseModel):
    """Complete AI configuration with prompts and model assignments"""
    prompts: List[AIPrompt] = []
    model_assignments: List[AIModelAssignment] = []
    
    class Config:
        from_attributes = True


# Enhanced schemas for content workspace
class ContentVariantDetail(BaseModel):
    id: int
    platform_name: str
    status: str
    content_preview: str
    created_at: datetime

    class Config:
        from_attributes = True


class SuggestedTopicDetail(BaseModel):
    id: int
    title: str
    description: Optional[str]
    category: str
    is_correlated: bool
    parent_topic_title: Optional[str]

    class Config:
        from_attributes = True


class ContentPlanSummary(BaseModel):
    id: int
    plan_period: str

    class Config:
        from_attributes = True


class ContentDraftWithDetails(BaseModel):
    id: int
    suggested_topic: SuggestedTopicDetail
    status: str
    variants: List[ContentVariantDetail]
    variants_count: int
    content_plan: ContentPlanSummary
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Advanced Content Generation Schemas
class ResearchRequest(BaseModel):
    """Request for topic research"""
    topic: str
    organizationId: Optional[int] = None
    industry: Optional[str] = None
    depth: Optional[str] = 'basic'  # basic, deep, comprehensive
    includeRawData: Optional[bool] = False
    storeResults: Optional[bool] = False

class ResearchResponse(BaseModel):
    """Response from research operation"""
    topic: str
    insights: Dict[str, Any]
    sources: List[Dict[str, Any]]
    keywords: List[str]
    relatedTopics: List[str]
    timestamp: datetime
    researchDepth: str
    rawData: Optional[Dict[str, Any]] = None

class GenerationInsights(BaseModel):
    """Insights from content generation process"""
    planId: int
    reasoningSteps: Optional[List[Dict[str, Any]]] = None
    researchResults: Optional[List[Dict[str, Any]]] = None
    briefAnalysis: Optional[Dict[str, Any]] = None
    qualityMetrics: Optional[Dict[str, Any]] = None
    generationMethod: str
    timestamp: datetime
