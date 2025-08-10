"""
CRUD operations for content briefs and correlation rules
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.db.models import ContentBrief, ContentCorrelationRule
from app.db.schemas_content_brief import (
    ContentBriefCreate, ContentBriefUpdate,
    CorrelationRuleCreate, CorrelationRuleUpdate
)


class ContentBriefCRUD:
    """CRUD operations for content briefs"""
    
    def create(self, db: Session, obj_in: ContentBriefCreate) -> ContentBrief:
        """Create a new content brief"""
        db_obj = ContentBrief(
            content_plan_id=obj_in.content_plan_id,
            title=obj_in.title,
            description=obj_in.description,
            priority_level=obj_in.priority_level,
            file_type=obj_in.file_type
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_id(self, db: Session, brief_id: int) -> Optional[ContentBrief]:
        """Get brief by ID"""
        return db.query(ContentBrief).filter(ContentBrief.id == brief_id).first()
    
    def get_by_content_plan(self, db: Session, content_plan_id: int) -> List[ContentBrief]:
        """Get all briefs for a content plan"""
        return db.query(ContentBrief).filter(
            ContentBrief.content_plan_id == content_plan_id
        ).order_by(ContentBrief.priority_level.desc()).all()
    
    def update(self, db: Session, brief_id: int, obj_in: ContentBriefUpdate) -> Optional[ContentBrief]:
        """Update a content brief"""
        db_obj = self.get_by_id(db, brief_id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def update_ai_analysis(self, db: Session, brief_id: int, 
                          extracted_content: str, key_topics: List[str], 
                          ai_analysis: Dict[str, Any]) -> Optional[ContentBrief]:
        """Update AI analysis results"""
        db_obj = self.get_by_id(db, brief_id)
        if not db_obj:
            return None
        
        db_obj.extracted_content = extracted_content
        db_obj.key_topics = key_topics
        db_obj.ai_analysis = ai_analysis
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def delete(self, db: Session, brief_id: int) -> bool:
        """Delete a content brief"""
        db_obj = self.get_by_id(db, brief_id)
        if not db_obj:
            return False
        
        db.delete(db_obj)
        db.commit()
        return True


class CorrelationRuleCRUD:
    """CRUD operations for correlation rules"""
    
    def create(self, db: Session, obj_in: CorrelationRuleCreate) -> ContentCorrelationRule:
        """Create correlation rules for a content plan"""
        db_obj = ContentCorrelationRule(**obj_in.dict())
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def get_by_content_plan(self, db: Session, content_plan_id: int) -> Optional[ContentCorrelationRule]:
        """Get correlation rules for a content plan"""
        return db.query(ContentCorrelationRule).filter(
            ContentCorrelationRule.content_plan_id == content_plan_id
        ).first()
    
    def update(self, db: Session, content_plan_id: int, 
               obj_in: CorrelationRuleUpdate) -> Optional[ContentCorrelationRule]:
        """Update correlation rules"""
        db_obj = self.get_by_content_plan(db, content_plan_id)
        if not db_obj:
            return None
        
        update_data = obj_in.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        
        db.commit()
        db.refresh(db_obj)
        return db_obj
    
    def calculate_total_sm_posts(self, db: Session, content_plan_id: int, 
                                blog_posts_count: int) -> Dict[str, int]:
        """Calculate total SM posts based on correlation rules"""
        rules = self.get_by_content_plan(db, content_plan_id)
        if not rules:
            # Default behavior if no rules exist
            return {
                "blog_correlated": blog_posts_count * 2,
                "brief_correlated": 0,
                "standalone": 0,
                "total": blog_posts_count * 2
            }
        
        blog_correlated = blog_posts_count * rules.sm_posts_per_blog
        brief_correlated = rules.brief_based_sm_posts
        standalone = rules.standalone_sm_posts
        
        return {
            "blog_correlated": blog_correlated,
            "brief_correlated": brief_correlated,
            "standalone": standalone,
            "total": blog_correlated + brief_correlated + standalone
        }


# Singleton instances
content_brief_crud = ContentBriefCRUD()
correlation_rule_crud = CorrelationRuleCRUD()