export interface User {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  avatar_url?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  last_login?: string;
}

export interface Organization {
  id: number;
  name: string;
  slug: string;
  description?: string;
  website?: string;
  industry?: string;
  size?: string;
  is_active: boolean;
  owner_id: number;
  created_at: string;
  updated_at: string;
}

export interface OrganizationCreate {
  name: string;
  description?: string;
  website?: string;
  industry?: string;
  size?: string;
}

export interface OrganizationUpdate {
  name?: string;
  description?: string;
  website?: string;
  industry?: string;
  size?: string;
}

export interface OrganizationWithMembers extends Organization {
  members: User[];
  owner: User;
}

export interface WebsiteAnalysis {
  id: number;
  organization_id: number;
  website_url: string;
  analysis_data?: any;
  
  // Basic analysis fields
  industry_detected?: string;
  services_detected?: string[];
  company_values?: string[];
  target_audience?: string[];
  content_tone?: string;
  key_topics?: string[];
  competitors_mentioned?: string[];
  
  // Enhanced AI analysis fields
  company_overview?: string;
  unique_selling_points?: string[];
  content_strategy_insights?: string;
  recommended_content_topics?: string[];
  brand_personality?: string;
  key_differentiators?: string[];
  market_positioning?: string;
  customer_pain_points?: string[];
  technology_stack?: string[];
  partnership_ecosystem?: string[];
  
  // Status and metadata
  last_analysis_date?: string;
  analysis_status: 'pending' | 'processing' | 'completed' | 'failed';
  error_message?: string;
  created_at: string;
  updated_at: string;
}

export interface Project {
  id: number;
  name: string;
  description?: string;
  organization_id: number;
  is_active: boolean;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  organization_id: number;
  project_id?: number;
  budget?: number;
  target_audience?: string;
  start_date?: string;
  end_date?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export enum TaskStatus {
  PENDING = "pending",
  IN_PROGRESS = "in_progress",
  COMPLETED = "completed",
  CANCELLED = "cancelled"
}

export enum TaskPriority {
  LOW = "low",
  MEDIUM = "medium",
  HIGH = "high",
  URGENT = "urgent"
}

export interface Task {
  id: number;
  title: string;
  description?: string;
  status: TaskStatus;
  priority: TaskPriority;
  organization_id: number;
  project_id?: number;
  campaign_id?: number;
  assignee_id?: number;
  created_by_id: number;
  due_date?: string;
  completed_at?: string;
  created_at: string;
  updated_at: string;
  task_type?: string;
  estimated_hours?: number;
  actual_hours?: number;
  tags?: string;
}

export interface TaskWithDetails extends Task {
  assignee?: User;
  creator: User;
  organization: Organization;
  project?: Project;
  campaign?: Campaign;
}

export interface DashboardStats {
  total_tasks: number;
  pending_tasks: number;
  in_progress_tasks: number;
  completed_tasks: number;
  overdue_tasks: number;
  total_projects: number;
  active_campaigns: number;
  organization_members: number;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  password: string;
  avatar_url?: string;
}

export interface TaskCreate {
  title: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  organization_id: number;
  project_id?: number;
  campaign_id?: number;
  assignee_id?: number;
  due_date?: string;
  task_type?: string;
  estimated_hours?: number;
  tags?: string;
}

export interface TaskUpdate {
  title?: string;
  description?: string;
  status?: TaskStatus;
  priority?: TaskPriority;
  due_date?: string;
  assignee_id?: number;
  task_type?: string;
  estimated_hours?: number;
  actual_hours?: number;
  tags?: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
}

export enum UserRole {
  OWNER = "owner",
  ADMIN = "admin",
  MEMBER = "member"
}

// Communication Strategy types
export interface CommunicationStrategy {
  id: number;
  name: string;
  description?: string;
  organization_id: number;
  created_by_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  communication_goals: string[];
  target_audiences: TargetAudience[];
  general_style: GeneralStyle;
  platform_styles: PlatformStyle[];
  forbidden_phrases: string[];
  preferred_phrases: string[];
  cta_rules: CTARule[];
  sample_content_types: string[];
}

export interface TargetAudience {
  id: number;
  name: string;
  description: string;
}

export interface GeneralStyle {
  language: string;
  tone: string;
  technical_content: string;
  employer_branding_content: string;
}

export interface PlatformStyle {
  id: number;
  platform_name: string;
  length_description: string;
  style_description: string;
  notes?: string;
}

export interface CTARule {
  id: number;
  content_type: string;
  cta_text: string;
}

export interface StrategyUploadResponse {
  task_id: string;
  status: string;
  message: string;
  file_name: string;
  file_size: number;
  file_type: string;
  organization_id: number;
}

export interface StrategyTaskStatus {
  task_id: string;
  status: 'PENDING' | 'PROGRESS' | 'SUCCESS' | 'FAILURE';
  result?: {
    status: 'SUCCESS' | 'FAILED';
    strategy_id?: number;
    organization_id: number;
    task_id: string;
    message: string;
    error?: string;
  };
  client_id: number;
  current?: number;
  total?: number;
}

// Content Plan types
export interface ContentPlan {
  id: number;
  plan_period: string;
  blog_posts_quota: number;
  sm_posts_quota: number;
  correlate_posts: boolean;
  scheduling_mode: string;
  scheduling_preferences?: string;
  brief_file_path?: string;
  status: string;
  organization_id: number;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  meta_data?: any;
}

export interface ContentPlanCreate {
  plan_period: string;
  blog_posts_quota: number;
  sm_posts_quota: number;
  correlate_posts: boolean;
  scheduling_mode?: string;
  scheduling_preferences?: string;
  organization_id: number;
  meta_data?: any;
}

export interface ContentPlanUpdate {
  plan_period?: string;
  blog_posts_quota?: number;
  sm_posts_quota?: number;
  correlate_posts?: boolean;
  scheduling_mode?: string;
  scheduling_preferences?: string;
  status?: string;
}

export type SchedulingMode = 'auto' | 'with_guidelines' | 'visual';

export interface SchedulingGuidelines {
  days_of_week: string[];
  preferred_times: string[];
  avoid_dates: string[];
}

export interface ContentPlanWizardData {
  // Step 1: Plan Definition
  plan_period: string;
  blog_posts_quota: number;
  sm_posts_quota: number;
  
  // Step 2: Context and Strategy
  monthly_brief_file?: File;
  correlate_posts: boolean;
  
  // Step 3: Schedule
  scheduling_mode?: SchedulingMode;
  scheduling_guidelines?: SchedulingGuidelines;
}

// SuggestedTopic types
export interface SuggestedTopic {
  id: number;
  content_plan_id: number;
  title: string;
  description?: string;
  category?: string;
  status: string;
  parent_topic_id?: number;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  meta_data?: any;
}

export interface TopicStatusUpdate {
  status: 'suggested' | 'approved' | 'rejected';
}

export interface ContentDraft {
  id: number;
  suggested_topic_id: number;
  topic?: string;
  status: ContentStatus;
  created_by_task_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  scheduled_for?: string;
  content_type?: string;
  variants_count?: number;
  suggested_topic?: SuggestedTopic;
  variants?: ContentVariant[];
  revisions?: DraftRevision[];
}

export interface ContentVariant {
  id: number;
  content_draft_id: number;
  platform_name: string;
  platform: string;
  content_text: string;
  status: ContentStatus;
  version: number;
  created_by_task_id?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  content_draft?: ContentDraft;
  meta_data?: any;
}

export interface DraftRevision {
  id: number;
  content_draft_id: number;
  revision_type: 'feedback' | 'regenerate' | 'initial';
  feedback_text?: string;
  previous_content?: string;
  revision_context?: string;
  created_by_user_id?: number;
  task_id?: string;
  created_at: string;
}

export interface VariantStatusUpdate {
  status: 'pending_approval' | 'approved' | 'rejected' | 'needs_revision';
}

export interface VariantRevisionRequest {
  feedback: string;
}

export interface VariantContentUpdate {
  content_text: string;
}

// Content Status types
export type ContentStatus = 'draft' | 'review' | 'approved' | 'rejected' | 'pending_approval' | 'needs_revision';

// Scheduled Post types
export interface ScheduledPost {
  id: number;
  content_variant_id: number;
  platform: string;
  scheduled_for: string;
  status: 'scheduled' | 'published' | 'failed' | 'cancelled';
  published_at?: string;
  external_post_id?: string;
  error_message?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  content_variant?: ContentVariant;
}

// Extended ContentDraft with scheduled_for
export interface ContentDraftWithSchedule extends ContentDraft {
  topic: string;
  content_type?: string;
  scheduled_for?: string;
  status: ContentStatus;
}

// Extended ContentVariant with platform
export interface ContentVariantWithPlatform extends ContentVariant {
  platform: string;
  content_draft?: ContentDraftWithSchedule;
}

// Extended ContentPlan with drafts
export interface ContentPlanWithDrafts extends ContentPlan {
  content_drafts?: ContentDraftWithSchedule[];
  status: 'draft' | 'in_progress' | 'complete';
}

// Content Brief types
export interface ContentBrief {
  id: number;
  content_plan_id: number;
  title: string;
  description?: string;
  key_topics?: string[];
  target_keywords?: string[];
  reference_materials?: string[];
  tone_guidelines?: string;
  special_instructions?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// Correlation Rule types
export interface CorrelationRule {
  id?: number;
  content_plan_id?: number;
  rule_type: string;
  sm_posts_per_blog: number;
  brief_based_sm_posts: number;
  standalone_sm_posts: number;
  platform_rules?: Record<string, number>;
  correlation_strength: string;
  timing_strategy: string;
  is_active?: boolean;
  created_at?: string;
  updated_at?: string;
}
