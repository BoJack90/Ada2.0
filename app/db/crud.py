from sqlalchemy.orm import Session, selectinload, joinedload
from sqlalchemy import and_, or_, func
from typing import List, Optional
from app.db import models, schemas
from app.core.security import get_password_hash, verify_password
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserCRUD:
    def get_by_email(self, db: Session, email: str) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.email == email).first()
    
    def get_by_username(self, db: Session, username: str) -> Optional[models.User]:
        return db.query(models.User).options(
            joinedload(models.User.organizations)
        ).filter(models.User.username == username).first()
    
    def get_by_id(self, db: Session, user_id: int) -> Optional[models.User]:
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    def create(self, db: Session, user_create: schemas.UserCreate) -> models.User:
        hashed_password = get_password_hash(user_create.password)
        db_user = models.User(
            email=user_create.email,
            username=user_create.username,
            first_name=user_create.first_name,
            last_name=user_create.last_name,
            password_hash=hashed_password,
            avatar_url=user_create.avatar_url
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    def authenticate(self, db: Session, username: str, password: str) -> Optional[models.User]:
        user = self.get_by_username(db, username) or self.get_by_email(db, username)
        if not user or not verify_password(password, user.password_hash):
            return None
        return user
    
    def update_last_login(self, db: Session, user: models.User):
        user.last_login = datetime.utcnow()
        db.commit()
        db.refresh(user)

class OrganizationCRUD:
    def get_by_id(self, db: Session, org_id: int) -> Optional[models.Organization]:
        return db.query(models.Organization).filter(models.Organization.id == org_id).first()
    
    def get_by_slug(self, db: Session, slug: str) -> Optional[models.Organization]:
        return db.query(models.Organization).filter(models.Organization.slug == slug).first()
    
    def get_user_organizations(self, db: Session, user_id: int) -> List[models.Organization]:
        return db.query(models.Organization).join(
            models.user_organization
        ).filter(models.user_organization.c.user_id == user_id).all()
    
    def create(self, db: Session, org_create: schemas.OrganizationCreate, owner_id: int) -> models.Organization:
        # Generate slug from name
        import re
        slug = re.sub(r'[^a-zA-Z0-9\s\-]', '', org_create.name.lower())
        slug = re.sub(r'[\s\-]+', '-', slug).strip('-')
        
        # Ensure slug is unique
        base_slug = slug
        counter = 1
        while db.query(models.Organization).filter(models.Organization.slug == slug).first():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        db_org = models.Organization(
            name=org_create.name,
            slug=slug,
            description=org_create.description,
            website=org_create.website,
            industry=org_create.industry,
            size=org_create.size,
            owner_id=owner_id
        )
        db.add(db_org)
        db.commit()
        db.refresh(db_org)
        
        # Add owner as member with owner role
        self.add_member(db, db_org.id, owner_id, "owner")
        return db_org
    
    def add_member(self, db: Session, org_id: int, user_id: int, role: str = "member"):
        # Check if already member
        existing = db.execute(
            models.user_organization.select().where(
                and_(
                    models.user_organization.c.organization_id == org_id,
                    models.user_organization.c.user_id == user_id
                )
            )
        ).first()
        
        if not existing:
            db.execute(
                models.user_organization.insert().values(
                    organization_id=org_id,
                    user_id=user_id,
                    role=role
                )
            )
            db.commit()
    
    def remove_member(self, db: Session, org_id: int, user_id: int):
        db.execute(
            models.user_organization.delete().where(
                and_(
                    models.user_organization.c.organization_id == org_id,
                    models.user_organization.c.user_id == user_id
                )
            )
        )
        db.commit()
    
    def get_members(self, db: Session, org_id: int) -> List[models.User]:
        return db.query(models.User).join(
            models.user_organization
        ).filter(models.user_organization.c.organization_id == org_id).all()
    
    def user_has_access(self, db: Session, org_id: int, user_id: int) -> bool:
        result = db.execute(
            models.user_organization.select().where(
                and_(
                    models.user_organization.c.organization_id == org_id,
                    models.user_organization.c.user_id == user_id
                )
            )
        ).first()
        return result is not None

class ProjectCRUD:
    def get_by_id(self, db: Session, project_id: int) -> Optional[models.Project]:
        return db.query(models.Project).filter(models.Project.id == project_id).first()
    
    def get_organization_projects(self, db: Session, org_id: int) -> List[models.Project]:
        return db.query(models.Project).filter(
            models.Project.organization_id == org_id,
            models.Project.is_active == True
        ).all()
    
    def create(self, db: Session, project_create: schemas.ProjectCreate) -> models.Project:
        db_project = models.Project(**project_create.dict())
        db.add(db_project)
        db.commit()
        db.refresh(db_project)
        return db_project

class CampaignCRUD:
    def get_by_id(self, db: Session, campaign_id: int) -> Optional[models.Campaign]:
        return db.query(models.Campaign).filter(models.Campaign.id == campaign_id).first()
    
    def get_organization_campaigns(self, db: Session, org_id: int) -> List[models.Campaign]:
        return db.query(models.Campaign).filter(
            models.Campaign.organization_id == org_id,
            models.Campaign.is_active == True
        ).all()
    
    def create(self, db: Session, campaign_create: schemas.CampaignCreate) -> models.Campaign:
        db_campaign = models.Campaign(**campaign_create.dict())
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

class TaskCRUD:
    def get_by_id(self, db: Session, task_id: int) -> Optional[models.Task]:
        return db.query(models.Task).options(
            selectinload(models.Task.assignee),
            selectinload(models.Task.creator),
            selectinload(models.Task.organization),
            selectinload(models.Task.project),
            selectinload(models.Task.campaign)
        ).filter(models.Task.id == task_id).first()
    
    def get_organization_tasks(self, db: Session, org_id: int, 
                              status: Optional[str] = None,
                              assignee_id: Optional[int] = None,
                              project_id: Optional[int] = None,
                              campaign_id: Optional[int] = None) -> List[models.Task]:
        query = db.query(models.Task).filter(models.Task.organization_id == org_id)
        
        if status:
            query = query.filter(models.Task.status == status)
        if assignee_id:
            query = query.filter(models.Task.assignee_id == assignee_id)
        if project_id:
            query = query.filter(models.Task.project_id == project_id)
        if campaign_id:
            query = query.filter(models.Task.campaign_id == campaign_id)
            
        return query.options(
            selectinload(models.Task.assignee),
            selectinload(models.Task.creator)
        ).all()
    
    def get_user_tasks(self, db: Session, user_id: int, org_id: Optional[int] = None) -> List[models.Task]:
        query = db.query(models.Task).filter(models.Task.assignee_id == user_id)
        
        if org_id:
            query = query.filter(models.Task.organization_id == org_id)
            
        return query.options(
            selectinload(models.Task.organization),
            selectinload(models.Task.project),
            selectinload(models.Task.campaign)
        ).all()
    
    def create(self, db: Session, task_create: schemas.TaskCreate, created_by_id: int) -> models.Task:
        db_task = models.Task(
            **task_create.dict(),
            created_by_id=created_by_id
        )
        db.add(db_task)
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def update(self, db: Session, task_id: int, task_update: schemas.TaskUpdate) -> Optional[models.Task]:
        db_task = db.query(models.Task).filter(models.Task.id == task_id).first()
        if not db_task:
            return None
            
        update_data = task_update.dict(exclude_unset=True)
        
        # Handle status change to completed
        if update_data.get("status") == "completed" and db_task.status != "completed":
            update_data["completed_at"] = datetime.utcnow()
        elif update_data.get("status") != "completed" and db_task.status == "completed":
            update_data["completed_at"] = None
        
        for field, value in update_data.items():
            setattr(db_task, field, value)
        
        db.commit()
        db.refresh(db_task)
        return db_task
    
    def get_dashboard_stats(self, db: Session, org_id: int) -> dict:
        total_tasks = db.query(models.Task).filter(models.Task.organization_id == org_id).count()
        
        pending_tasks = db.query(models.Task).filter(
            models.Task.organization_id == org_id,
            models.Task.status == "pending"
        ).count()
        
        in_progress_tasks = db.query(models.Task).filter(
            models.Task.organization_id == org_id,
            models.Task.status == "in_progress"
        ).count()
        
        completed_tasks = db.query(models.Task).filter(
            models.Task.organization_id == org_id,
            models.Task.status == "completed"
        ).count()
        
        overdue_tasks = db.query(models.Task).filter(
            models.Task.organization_id == org_id,
            models.Task.due_date < datetime.utcnow(),
            models.Task.status.in_(["pending", "in_progress"])
        ).count()
        
        total_projects = db.query(models.Project).filter(
            models.Project.organization_id == org_id,
            models.Project.is_active == True
        ).count()
        
        active_campaigns = db.query(models.Campaign).filter(
            models.Campaign.organization_id == org_id,
            models.Campaign.is_active == True
        ).count()
        
        organization_members = db.execute(
            models.user_organization.select().where(
                models.user_organization.c.organization_id == org_id
            )
        ).rowcount
        
        return {
            "total_tasks": total_tasks,
            "pending_tasks": pending_tasks,
            "in_progress_tasks": in_progress_tasks,
            "completed_tasks": completed_tasks,
            "overdue_tasks": overdue_tasks,
            "total_projects": total_projects,
            "active_campaigns": active_campaigns,
            "organization_members": organization_members
        }

class ContentPlanCRUD:
    def get_by_id(self, db: Session, content_plan_id: int) -> Optional[models.ContentPlan]:
        return db.query(models.ContentPlan).filter(models.ContentPlan.id == content_plan_id).first()
    
    def get_organization_content_plans(self, db: Session, org_id: int) -> List[models.ContentPlan]:
        return db.query(models.ContentPlan).filter(
            models.ContentPlan.organization_id == org_id,
            models.ContentPlan.is_active == True
        ).all()
    
    def create(self, db: Session, content_plan_create: schemas.ContentPlanCreate) -> models.ContentPlan:
        # Ensure meta_data is at least an empty dict
        plan_data = content_plan_create.dict()
        if plan_data.get('meta_data') is None:
            plan_data['meta_data'] = {}
            logger.warning("ContentPlanCRUD: meta_data was None, setting to empty dict")
        else:
            logger.info(f"ContentPlanCRUD: Creating plan with meta_data: {plan_data.get('meta_data')}")
        
        db_content_plan = models.ContentPlan(**plan_data)
        db.add(db_content_plan)
        db.commit()
        db.refresh(db_content_plan)
        
        # Log the saved meta_data
        logger.info(f"ContentPlanCRUD: Saved content plan {db_content_plan.id} with meta_data: {db_content_plan.meta_data}")
        
        return db_content_plan
    
    def update(self, db: Session, content_plan_id: int, content_plan_update: schemas.ContentPlanUpdate) -> Optional[models.ContentPlan]:
        db_content_plan = db.query(models.ContentPlan).filter(models.ContentPlan.id == content_plan_id).first()
        if not db_content_plan:
            return None
            
        update_data = content_plan_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_content_plan, field, value)
        
        db.commit()
        db.refresh(db_content_plan)
        return db_content_plan
    
    def delete(self, db: Session, content_plan_id: int) -> bool:
        db_content_plan = db.query(models.ContentPlan).filter(models.ContentPlan.id == content_plan_id).first()
        if not db_content_plan:
            return False
        
        db_content_plan.is_active = False
        db.commit()
        return True
    
    def get_by_status(self, db: Session, org_id: int, status: str) -> List[models.ContentPlan]:
        return db.query(models.ContentPlan).filter(
            models.ContentPlan.organization_id == org_id,
            models.ContentPlan.status == status,
            models.ContentPlan.is_active == True
        ).all()


class SuggestedTopicCRUD:
    def get_by_id(self, db: Session, topic_id: int) -> Optional[models.SuggestedTopic]:
        return db.query(models.SuggestedTopic).options(
            selectinload(models.SuggestedTopic.content_plan)
        ).filter(models.SuggestedTopic.id == topic_id).first()
    
    def get_by_content_plan_id(self, db: Session, plan_id: int, status: Optional[str] = None) -> List[models.SuggestedTopic]:
        """
        Pobiera tematy związane z danym planem treści bezpośrednio przez content_plan_id
        """
        query = db.query(models.SuggestedTopic).filter(
            models.SuggestedTopic.content_plan_id == plan_id,
            models.SuggestedTopic.is_active == True
        )
        
        if status:
            query = query.filter(models.SuggestedTopic.status == status)
        
        return query.all()
    
    def get_organization_suggested_topics(self, db: Session, org_id: int, status: Optional[str] = None) -> List[models.SuggestedTopic]:
        query = db.query(models.SuggestedTopic).join(
            models.ContentPlan, models.SuggestedTopic.content_plan_id == models.ContentPlan.id
        ).filter(
            models.ContentPlan.organization_id == org_id,
            models.SuggestedTopic.is_active == True
        )
        
        if status:
            query = query.filter(models.SuggestedTopic.status == status)
        
        return query.all()
    
    def create(self, db: Session, topic_create: schemas.SuggestedTopicCreate) -> models.SuggestedTopic:
        db_topic = models.SuggestedTopic(**topic_create.dict())
        db.add(db_topic)
        db.commit()
        db.refresh(db_topic)
        return db_topic
    
    def update_status(self, db: Session, topic_id: int, status: str) -> Optional[models.SuggestedTopic]:
        db_topic = db.query(models.SuggestedTopic).filter(models.SuggestedTopic.id == topic_id).first()
        if not db_topic:
            return None
        
        db_topic.status = status
        db.commit()
        db.refresh(db_topic)
        return db_topic
    
    def update(self, db: Session, topic_id: int, topic_update: schemas.SuggestedTopicUpdate) -> Optional[models.SuggestedTopic]:
        db_topic = db.query(models.SuggestedTopic).filter(models.SuggestedTopic.id == topic_id).first()
        if not db_topic:
            return None
            
        update_data = topic_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_topic, field, value)
        
        db.commit()
        db.refresh(db_topic)
        return db_topic
    
    def count_by_status(self, db: Session, content_plan_id: int, status: str) -> int:
        return db.query(models.SuggestedTopic).filter(
            models.SuggestedTopic.content_plan_id == content_plan_id,
            models.SuggestedTopic.status == status,
            models.SuggestedTopic.is_active == True
        ).count()


class ContentDraftCRUD:
    def get_by_id(self, db: Session, draft_id: int) -> Optional[models.ContentDraft]:
        return db.query(models.ContentDraft).options(
            selectinload(models.ContentDraft.suggested_topic),
            selectinload(models.ContentDraft.variants),
            selectinload(models.ContentDraft.revisions)
        ).filter(models.ContentDraft.id == draft_id).first()
    
    def get_by_scheduled_post_id(self, db: Session, post_id: int, status: Optional[str] = None) -> List[models.ContentDraft]:
        query = db.query(models.ContentDraft).filter(
            models.ContentDraft.scheduled_post_id == post_id,
            models.ContentDraft.is_active == True
        )
        
        if status:
            query = query.filter(models.ContentDraft.status == status)
        
        return query.order_by(models.ContentDraft.version.desc()).all()
    
    def get_latest_version_by_post_id(self, db: Session, post_id: int) -> Optional[models.ContentDraft]:
        return db.query(models.ContentDraft).filter(
            models.ContentDraft.scheduled_post_id == post_id,
            models.ContentDraft.is_active == True
        ).order_by(models.ContentDraft.version.desc()).first()
    
    def get_drafts_by_content_plan_id(self, db: Session, plan_id: int, status: Optional[str] = None) -> List[models.ContentDraft]:
        """Get all drafts for a content plan through suggested topics"""
        from sqlalchemy.orm import joinedload
        
        query = db.query(models.ContentDraft).options(
            joinedload(models.ContentDraft.suggested_topic),
            joinedload(models.ContentDraft.variants)
        ).join(
            models.SuggestedTopic, models.ContentDraft.suggested_topic_id == models.SuggestedTopic.id
        ).filter(
            models.SuggestedTopic.content_plan_id == plan_id,
            models.ContentDraft.is_active == True
        )
        
        if status:
            query = query.filter(models.ContentDraft.status == status)
        
        return query.order_by(models.ContentDraft.created_at.desc()).all()
    
    def create(self, db: Session, draft_create: schemas.ContentDraftCreate) -> models.ContentDraft:
        # Get the next version number for this scheduled post
        latest_draft = self.get_latest_version_by_post_id(db, draft_create.scheduled_post_id)
        next_version = (latest_draft.version + 1) if latest_draft else 1
        
        db_draft = models.ContentDraft(
            **draft_create.dict(),
            version=next_version
        )
        db.add(db_draft)
        db.commit()
        db.refresh(db_draft)
        return db_draft
    
    def update_status(self, db: Session, draft_id: int, status: str) -> Optional[models.ContentDraft]:
        db_draft = db.query(models.ContentDraft).filter(models.ContentDraft.id == draft_id).first()
        if not db_draft:
            return None
        
        db_draft.status = status
        db_draft.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_draft)
        return db_draft
    
    def update(self, db: Session, draft_id: int, draft_update: schemas.ContentDraftUpdate) -> Optional[models.ContentDraft]:
        db_draft = db.query(models.ContentDraft).filter(models.ContentDraft.id == draft_id).first()
        if not db_draft:
            return None
        
        update_data = draft_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_draft, field, value)
        
        db_draft.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_draft)
        return db_draft
    
    def count_by_status(self, db: Session, plan_id: int, status: str) -> int:
        """Count drafts by status for a content plan"""
        return db.query(models.ContentDraft).join(
            models.ScheduledPost, models.ContentDraft.scheduled_post_id == models.ScheduledPost.id
        ).filter(
            models.ScheduledPost.content_plan_id == plan_id,
            models.ContentDraft.status == status,
            models.ContentDraft.is_active == True
        ).count()


class DraftRevisionCRUD:
    def get_by_id(self, db: Session, revision_id: int) -> Optional[models.DraftRevision]:
        return db.query(models.DraftRevision).filter(models.DraftRevision.id == revision_id).first()
    
    def get_by_content_draft_id(self, db: Session, draft_id: int) -> List[models.DraftRevision]:
        return db.query(models.DraftRevision).filter(
            models.DraftRevision.content_draft_id == draft_id
        ).order_by(models.DraftRevision.created_at.desc()).all()
    
    def create(self, db: Session, revision_create: schemas.DraftRevisionCreate) -> models.DraftRevision:
        db_revision = models.DraftRevision(**revision_create.dict())
        db.add(db_revision)
        db.commit()
        db.refresh(db_revision)
        return db_revision
    
    def get_latest_by_draft_id(self, db: Session, draft_id: int) -> Optional[models.DraftRevision]:
        return db.query(models.DraftRevision).filter(
            models.DraftRevision.content_draft_id == draft_id
        ).order_by(models.DraftRevision.created_at.desc()).first()


class ContentVariantCRUD:
    def get_by_id(self, db: Session, variant_id: int) -> Optional[models.ContentVariant]:
        return db.query(models.ContentVariant).filter(models.ContentVariant.id == variant_id).first()
    
    def get_by_content_draft_id(self, db: Session, draft_id: int) -> List[models.ContentVariant]:
        return db.query(models.ContentVariant).filter(
            models.ContentVariant.content_draft_id == draft_id,
            models.ContentVariant.is_active == True
        ).order_by(models.ContentVariant.created_at.desc()).all()
    
    def get_by_platform(self, db: Session, draft_id: int, platform_name: str) -> Optional[models.ContentVariant]:
        return db.query(models.ContentVariant).filter(
            models.ContentVariant.content_draft_id == draft_id,
            models.ContentVariant.platform_name == platform_name,
            models.ContentVariant.is_active == True
        ).first()
    
    def create(self, db: Session, variant_create: schemas.ContentVariantCreate) -> models.ContentVariant:
        db_variant = models.ContentVariant(**variant_create.dict())
        db.add(db_variant)
        db.commit()
        db.refresh(db_variant)
        return db_variant
    
    def update(self, db: Session, variant_id: int, variant_update: schemas.ContentVariantUpdate) -> Optional[models.ContentVariant]:
        db_variant = db.query(models.ContentVariant).filter(models.ContentVariant.id == variant_id).first()
        if not db_variant:
            return None
        
        update_data = variant_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_variant, field, value)
        
        db_variant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_variant)
        return db_variant
    
    def update_status(self, db: Session, variant_id: int, status: str) -> Optional[models.ContentVariant]:
        db_variant = db.query(models.ContentVariant).filter(models.ContentVariant.id == variant_id).first()
        if not db_variant:
            return None
        
        db_variant.status = status
        db_variant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_variant)
        return db_variant
    
    def update_content(self, db: Session, variant_id: int, content_text: str) -> Optional[models.ContentVariant]:
        db_variant = db.query(models.ContentVariant).filter(models.ContentVariant.id == variant_id).first()
        if not db_variant:
            return None
        
        db_variant.content_text = content_text
        db_variant.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_variant)
        return db_variant
    
    def count_by_status(self, db: Session, draft_id: int, status: str) -> int:
        return db.query(models.ContentVariant).filter(
            models.ContentVariant.content_draft_id == draft_id,
            models.ContentVariant.status == status,
            models.ContentVariant.is_active == True
        ).count()
    
    def get_approved_variants(self, db: Session, draft_id: int) -> List[models.ContentVariant]:
        """Get all approved variants for a draft"""
        return db.query(models.ContentVariant)\
            .filter(models.ContentVariant.draft_id == draft_id)\
            .filter(models.ContentVariant.status == "approved")\
            .all()


class AIPromptCRUD:
    """CRUD operations for AI prompts"""
    
    def get_by_id(self, db: Session, prompt_id: int) -> Optional[models.AIPrompt]:
        return db.query(models.AIPrompt).filter(models.AIPrompt.id == prompt_id).first()
    
    def get_by_name(self, db: Session, prompt_name: str) -> Optional[models.AIPrompt]:
        return db.query(models.AIPrompt)\
            .filter(models.AIPrompt.prompt_name == prompt_name)\
            .order_by(models.AIPrompt.version.desc())\
            .first()
    
    def get_all(self, db: Session) -> List[models.AIPrompt]:
        return db.query(models.AIPrompt)\
            .order_by(models.AIPrompt.prompt_name, models.AIPrompt.version.desc())\
            .all()
    
    def get_latest_versions(self, db: Session) -> List[models.AIPrompt]:
        """Get the latest version of each prompt"""
        return db.query(models.AIPrompt)\
            .filter(models.AIPrompt.version == db.query(func.max(models.AIPrompt.version))\
                   .filter(models.AIPrompt.prompt_name == models.AIPrompt.prompt_name))\
            .all()
    
    def create(self, db: Session, prompt_create: schemas.AIPromptCreate) -> models.AIPrompt:
        # Check if prompt with this name already exists
        existing_prompt = self.get_by_name(db, prompt_create.prompt_name)
        version = existing_prompt.version + 1 if existing_prompt else 1
        
        db_prompt = models.AIPrompt(
            prompt_name=prompt_create.prompt_name,
            prompt_template=prompt_create.prompt_template,
            version=version,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_prompt)
        db.commit()
        db.refresh(db_prompt)
        return db_prompt
    
    def update(self, db: Session, prompt_id: int, prompt_update: schemas.AIPromptUpdate) -> Optional[models.AIPrompt]:
        prompt = self.get_by_id(db, prompt_id)
        if not prompt:
            return None
        
        # Create new version for template updates
        if prompt_update.prompt_template:
            new_prompt = models.AIPrompt(
                prompt_name=prompt.prompt_name,
                prompt_template=prompt_update.prompt_template,
                version=prompt.version + 1,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(new_prompt)
            db.commit()
            db.refresh(new_prompt)
            return new_prompt
        
        return prompt
    
    def delete(self, db: Session, prompt_id: int) -> bool:
        prompt = self.get_by_id(db, prompt_id)
        if not prompt:
            return False
        
        db.delete(prompt)
        db.commit()
        return True


class AIModelAssignmentCRUD:
    """CRUD operations for AI model assignments"""
    
    def get_by_id(self, db: Session, assignment_id: int) -> Optional[models.AIModelAssignment]:
        return db.query(models.AIModelAssignment).filter(models.AIModelAssignment.id == assignment_id).first()
    
    def get_by_task_name(self, db: Session, task_name: str) -> Optional[models.AIModelAssignment]:
        return db.query(models.AIModelAssignment)\
            .filter(models.AIModelAssignment.task_name == task_name)\
            .first()
    
    def get_all(self, db: Session) -> List[models.AIModelAssignment]:
        return db.query(models.AIModelAssignment)\
            .order_by(models.AIModelAssignment.task_name)\
            .all()
    
    def create(self, db: Session, assignment_create: schemas.AIModelAssignmentCreate) -> models.AIModelAssignment:
        db_assignment = models.AIModelAssignment(
            task_name=assignment_create.task_name,
            model_name=assignment_create.model_name,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(db_assignment)
        db.commit()
        db.refresh(db_assignment)
        return db_assignment
    
    def update(self, db: Session, assignment_id: int, assignment_update: schemas.AIModelAssignmentUpdate) -> Optional[models.AIModelAssignment]:
        assignment = self.get_by_id(db, assignment_id)
        if not assignment:
            return None
        
        if assignment_update.model_name:
            assignment.model_name = assignment_update.model_name
        
        assignment.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(assignment)
        return assignment
    
    def delete(self, db: Session, assignment_id: int) -> bool:
        assignment = self.get_by_id(db, assignment_id)
        if not assignment:
            return False
        
        db.delete(assignment)
        db.commit()
        return True


# Create instances
user_crud = UserCRUD()
organization_crud = OrganizationCRUD()
project_crud = ProjectCRUD()
campaign_crud = CampaignCRUD()
task_crud = TaskCRUD()
content_plan_crud = ContentPlanCRUD()
suggested_topic_crud = SuggestedTopicCRUD()
content_draft_crud = ContentDraftCRUD()
draft_revision_crud = DraftRevisionCRUD()
content_variant_crud = ContentVariantCRUD()
ai_prompt_crud = AIPromptCRUD()
ai_model_assignment_crud = AIModelAssignmentCRUD()
