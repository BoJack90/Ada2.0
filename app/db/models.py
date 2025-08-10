from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, ForeignKey, Table, Enum, JSON, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from datetime import datetime
from typing import Optional

Base = declarative_base()

# Tabela łącząca użytkowników z organizacjami (many-to-many)
user_organization = Table(
    'user_organization',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('role', String(50), default='member'),  # owner, admin, member
    Column('joined_at', DateTime, default=func.now())
)

class TaskStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskPriority(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(100), unique=True, index=True, nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    avatar_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_login = Column(DateTime, nullable=True)
    
    # Relacje
    organizations = relationship("Organization", secondary=user_organization, back_populates="members")
    owned_organizations = relationship("Organization", back_populates="owner")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    created_tasks = relationship("Task", foreign_keys="Task.created_by_id", back_populates="creator")

class Organization(Base):
    __tablename__ = "organizations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    slug = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    website = Column(String(255), nullable=True)
    logo_url = Column(String(500), nullable=True)
    industry = Column(String(100), nullable=True)
    size = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje (na razie komentujemy, żeby nie było błędów)
    owner = relationship("User", back_populates="owned_organizations")
    members = relationship("User", secondary=user_organization, back_populates="organizations")
    custom_prompts = relationship("OrganizationAIPrompt", back_populates="organization", cascade="all, delete-orphan")
    custom_model_assignments = relationship("OrganizationAIModelAssignment", back_populates="organization", cascade="all, delete-orphan")
    website_analysis = relationship("WebsiteAnalysis", back_populates="organization", uselist=False, cascade="all, delete-orphan")
    # tasks = relationship("Task", back_populates="organization")
    # campaigns = relationship("Campaign", back_populates="organization")
    # projects = relationship("Project", back_populates="organization")

class Project(Base):
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    # organization = relationship("Organization", back_populates="projects")
    tasks = relationship("Task", back_populates="project")
    campaigns = relationship("Campaign", back_populates="project")

class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    budget = Column(Integer, nullable=True)  # w groszach/centach
    target_audience = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    # organization = relationship("Organization", back_populates="campaigns")
    project = relationship("Project", back_populates="campaigns")
    tasks = relationship("Task", back_populates="campaign")

class Task(Base):
    __tablename__ = "tasks"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(300), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    priority = Column(Enum(TaskPriority), default=TaskPriority.MEDIUM)
    
    # Relacje organizacyjne
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    campaign_id = Column(Integer, ForeignKey("campaigns.id"), nullable=True)
    
    # Kto za co odpowiada
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Terminy
    due_date = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Metadane marketingowe
    task_type = Column(String(100), nullable=True)  # content_creation, social_media, email_marketing, etc.
    estimated_hours = Column(Integer, nullable=True)
    actual_hours = Column(Integer, nullable=True)
    tags = Column(Text, nullable=True)  # JSON array of tags
    
    # Relacje
    # organization = relationship("Organization", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    campaign = relationship("Campaign", back_populates="tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")
    creator = relationship("User", foreign_keys=[created_by_id], back_populates="created_tasks")
    comments = relationship("TaskComment", back_populates="task")
    attachments = relationship("TaskAttachment", back_populates="task")

class TaskComment(Base):
    __tablename__ = "task_comments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    task = relationship("Task", back_populates="comments")
    user = relationship("User")

class TaskAttachment(Base):
    __tablename__ = "task_attachments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False)
    mime_type = Column(String(100), nullable=False)
    uploaded_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relacje
    task = relationship("Task", back_populates="attachments")
    uploaded_by = relationship("User")


class AIPrompt(Base):
    __tablename__ = "ai_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    prompt_name = Column(String(100), unique=True, index=True, nullable=False)
    prompt_template = Column(Text, nullable=False)
    description = Column(Text, nullable=True)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AIModelAssignment(Base):
    __tablename__ = "ai_model_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    task_name = Column(String(100), unique=True, index=True, nullable=False)
    model_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class OrganizationAIPrompt(Base):
    __tablename__ = "organization_ai_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    prompt_name = Column(String(100), nullable=False)
    prompt_template = Column(Text, nullable=False)
    base_prompt_id = Column(Integer, ForeignKey("ai_prompts.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    version = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="custom_prompts")
    base_prompt = relationship("AIPrompt")
    created_by = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'prompt_name', name='_org_prompt_uc'),
    )


class OrganizationAIModelAssignment(Base):
    __tablename__ = "organization_ai_model_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    task_name = Column(String(100), nullable=False)
    model_name = Column(String(100), nullable=False)
    base_assignment_id = Column(Integer, ForeignKey("ai_model_assignments.id", ondelete="SET NULL"), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    # Relationships
    organization = relationship("Organization", back_populates="custom_model_assignments")
    base_assignment = relationship("AIModelAssignment")
    created_by = relationship("User")
    
    __table_args__ = (
        UniqueConstraint('organization_id', 'task_name', name='_org_model_uc'),
    )


# Content Generation Models
class CommunicationStrategy(Base):
    __tablename__ = "communication_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    creator = relationship("User")
    personas = relationship("Persona", back_populates="communication_strategy")
    platform_styles = relationship("PlatformStyle", back_populates="communication_strategy")
    cta_rules = relationship("CTARule", back_populates="communication_strategy")
    general_style = relationship("GeneralStyle", back_populates="communication_strategy", uselist=False)


class Persona(Base):
    __tablename__ = "personas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy", back_populates="personas")


class PlatformStyle(Base):
    __tablename__ = "platform_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    platform_name = Column(String(100), nullable=False)
    length_description = Column(Text, nullable=False)
    style_description = Column(Text, nullable=False)
    notes = Column(Text, nullable=True)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy", back_populates="platform_styles")


class CTARule(Base):
    __tablename__ = "cta_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(100), nullable=False)
    cta_text = Column(String(500), nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy", back_populates="cta_rules")


class GeneralStyle(Base):
    __tablename__ = "general_styles"
    
    id = Column(Integer, primary_key=True, index=True)
    language = Column(String(200), nullable=False)
    tone = Column(String(500), nullable=False)
    technical_content = Column(Text, nullable=False)
    employer_branding_content = Column(Text, nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy", back_populates="general_style")


class CommunicationGoal(Base):
    __tablename__ = "communication_goals"
    
    id = Column(Integer, primary_key=True, index=True)
    goal_text = Column(String(500), nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy")


class ForbiddenPhrase(Base):
    __tablename__ = "forbidden_phrases"
    
    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String(200), nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy")


class PreferredPhrase(Base):
    __tablename__ = "preferred_phrases"
    
    id = Column(Integer, primary_key=True, index=True)
    phrase = Column(String(200), nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy")


class SampleContentType(Base):
    __tablename__ = "sample_content_types"
    
    id = Column(Integer, primary_key=True, index=True)
    content_type = Column(String(100), nullable=False)
    communication_strategy_id = Column(Integer, ForeignKey("communication_strategies.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    
    # Relacje
    communication_strategy = relationship("CommunicationStrategy")


# Content Planning Models
class SuggestedTopic(Base):
    __tablename__ = "suggested_topics"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    category = Column(String(100), nullable=True)
    status = Column(String(50), default='suggested', nullable=False)  # suggested, approved, rejected
    content_plan_id = Column(Integer, ForeignKey("content_plans.id"), nullable=False)
    parent_topic_id = Column(Integer, ForeignKey("suggested_topics.id"), nullable=True)
    meta_data = Column(JSON, nullable=True)  # Store reasoning data, priority scores, etc.
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    content_plan = relationship("ContentPlan", back_populates="suggested_topics")
    parent = relationship("SuggestedTopic", remote_side=[id], back_populates="children")
    children = relationship("SuggestedTopic", back_populates="parent")
    content_drafts = relationship("ContentDraft", back_populates="suggested_topic")


class ContentPlan(Base):
    __tablename__ = "content_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_period = Column(String(100), nullable=False)
    blog_posts_quota = Column(Integer, nullable=False)
    sm_posts_quota = Column(Integer, nullable=False)
    correlate_posts = Column(Boolean, default=True)
    scheduling_mode = Column(String(50), default='auto')
    scheduling_preferences = Column(Text, nullable=True)
    brief_file_path = Column(String(500), nullable=True)  # Path to uploaded brief file
    meta_data = Column(JSON, nullable=True)  # Store generation settings, method used, etc.
    status = Column(String(50), default='new', nullable=False)  # new, generating_topics, pending_blog_topic_approval, generating_sm_topics, complete
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    scheduled_posts = relationship("ScheduledPost", back_populates="content_plan")
    suggested_topics = relationship("SuggestedTopic", back_populates="content_plan")
    briefs = relationship("ContentBrief", back_populates="content_plan", cascade="all, delete-orphan")
    correlation_rules = relationship("ContentCorrelationRule", back_populates="content_plan", cascade="all, delete-orphan")


class ScheduledPost(Base):
    __tablename__ = "scheduled_posts"
    
    id = Column(Integer, primary_key=True, index=True)
    publication_date = Column(DateTime, nullable=False)
    status = Column(String(50), default='scheduled', nullable=False)
    post_type = Column(String(50), nullable=True)
    title = Column(String(200), nullable=True)
    content = Column(Text, nullable=True)  # Deprecated - content now comes from ContentVariant
    platform = Column(String(100), nullable=True)  # Deprecated - platform now comes from ContentVariant
    content_plan_id = Column(Integer, ForeignKey("content_plans.id"), nullable=False)
    content_variant_id = Column(Integer, ForeignKey("content_variants.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    content_plan = relationship("ContentPlan", back_populates="scheduled_posts")
    content_variant = relationship("ContentVariant", back_populates="scheduled_posts")


# Content Draft Models
class ContentDraft(Base):
    __tablename__ = "content_drafts"
    
    id = Column(Integer, primary_key=True, index=True)
    suggested_topic_id = Column(Integer, ForeignKey("suggested_topics.id"), nullable=False)
    status = Column(String(50), default='drafting', nullable=False)  # drafting, pending_approval, approved, rejected
    created_by_task_id = Column(String(100), nullable=True)  # Celery task ID for tracking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    suggested_topic = relationship("SuggestedTopic")
    variants = relationship("ContentVariant", back_populates="draft", cascade="all, delete-orphan")
    revisions = relationship("DraftRevision", back_populates="content_draft", order_by="DraftRevision.created_at.desc()")


class ContentVariant(Base):
    __tablename__ = "content_variants"
    
    id = Column(Integer, primary_key=True, index=True)
    content_draft_id = Column(Integer, ForeignKey("content_drafts.id"), nullable=False)
    platform_name = Column(String(100), nullable=False)  # linkedin, facebook, instagram, wordpress, blog
    content_text = Column(Text, nullable=False)
    headline = Column(String(500), nullable=True)  # Optional headline/title
    cta_text = Column(String(500), nullable=True)  # Call to action
    hashtags = Column(JSON, nullable=True)  # List of hashtags
    media_suggestions = Column(JSON, nullable=True)  # Suggested media/images
    meta_data = Column(JSON, nullable=True)  # Quality metrics, SEO data, etc.
    status = Column(String(50), default='pending_approval', nullable=False)  # pending_approval, approved, rejected, needs_revision
    version = Column(Integer, default=1, nullable=False)
    created_by_task_id = Column(String(100), nullable=True)  # Celery task ID for tracking
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relacje
    draft = relationship("ContentDraft", back_populates="variants")
    scheduled_posts = relationship("ScheduledPost", back_populates="content_variant")


class DraftRevision(Base):
    __tablename__ = "draft_revisions"
    
    id = Column(Integer, primary_key=True, index=True)
    content_draft_id = Column(Integer, ForeignKey("content_drafts.id"), nullable=False)
    revision_type = Column(String(50), nullable=False)  # feedback, regenerate, initial
    feedback_text = Column(Text, nullable=True)  # Operator feedback for revision
    previous_content = Column(Text, nullable=True)  # Previous version content for reference
    revision_context = Column(Text, nullable=True)  # Additional context as JSON
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User who requested revision
    task_id = Column(String(100), nullable=True)  # Celery task ID
    created_at = Column(DateTime, default=func.now())
    
    # Relacje
    content_draft = relationship("ContentDraft", back_populates="revisions")
    created_by = relationship("User")


# Content Brief Models
class ContentBrief(Base):
    """Briefs attached to content plans with priority information"""
    __tablename__ = "content_briefs"
    
    id = Column(Integer, primary_key=True, index=True)
    content_plan_id = Column(Integer, ForeignKey("content_plans.id"), nullable=False)
    
    # Brief metadata
    title = Column(String(200), nullable=False)
    description = Column(Text)
    file_path = Column(String(500))  # Path to uploaded file
    file_type = Column(String(50))  # PDF, DOCX, TXT, etc.
    
    # Content extraction
    extracted_content = Column(Text)  # Extracted text from file
    key_topics = Column(JSON)  # AI-extracted key topics
    priority_level = Column(Integer, default=5)  # 1-10 priority scale
    
    # AI Analysis results
    ai_analysis = Column(JSON)  # Structured analysis from AI
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    content_plan = relationship("ContentPlan", back_populates="briefs")


class ContentCorrelationRule(Base):
    """Advanced correlation rules for content planning"""
    __tablename__ = "content_correlation_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    content_plan_id = Column(Integer, ForeignKey("content_plans.id"), nullable=False)
    
    # Correlation configuration
    rule_type = Column(String(50))  # 'blog_to_sm', 'brief_to_sm', 'standalone'
    
    # For blog_to_sm correlations
    sm_posts_per_blog = Column(Integer, default=2)
    
    # For brief_to_sm correlations
    brief_based_sm_posts = Column(Integer, default=0)
    
    # Standalone posts
    standalone_sm_posts = Column(Integer, default=0)
    
    # Platform-specific rules
    platform_rules = Column(JSON)  # {"linkedin": 2, "facebook": 1, etc.}
    
    # Advanced settings
    correlation_strength = Column(String(20), default="moderate")  # tight, moderate, loose
    timing_strategy = Column(String(50), default="distributed")  # distributed, clustered, sequential
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    content_plan = relationship("ContentPlan", back_populates="correlation_rules")


class ResearchResult(Base):
    """Store research results from external sources"""
    __tablename__ = "research_results"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id"), nullable=False)
    topic = Column(String(500), nullable=False, index=True)
    research_data = Column(JSON, nullable=False)
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization")
    created_by = relationship("User")


class WebsiteAnalysis(Base):
    """Store website analysis results for organizations"""
    __tablename__ = "website_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    organization_id = Column(Integer, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False, unique=True)
    website_url = Column(String(500), nullable=False)
    analysis_data = Column(JSON, nullable=True)
    
    # Basic analysis fields
    industry_detected = Column(String(200), nullable=True)
    services_detected = Column(JSON, nullable=True)
    company_values = Column(JSON, nullable=True)
    target_audience = Column(JSON, nullable=True)
    content_tone = Column(String(200), nullable=True)
    key_topics = Column(JSON, nullable=True)
    competitors_mentioned = Column(JSON, nullable=True)
    
    # Enhanced AI analysis fields
    company_overview = Column(Text, nullable=True)
    unique_selling_points = Column(JSON, nullable=True)
    content_strategy_insights = Column(Text, nullable=True)
    recommended_content_topics = Column(JSON, nullable=True)
    brand_personality = Column(Text, nullable=True)
    key_differentiators = Column(JSON, nullable=True)
    market_positioning = Column(String(500), nullable=True)
    customer_pain_points = Column(JSON, nullable=True)
    technology_stack = Column(JSON, nullable=True)
    partnership_ecosystem = Column(JSON, nullable=True)
    
    # Status and metadata
    last_analysis_date = Column(DateTime, nullable=True)
    analysis_status = Column(String(50), default='pending', nullable=False)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    organization = relationship("Organization", back_populates="website_analysis")
