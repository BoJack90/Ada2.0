import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from celery import current_app
from sqlalchemy.orm import Session

from app.tasks.celery_app import celery_app
from app.db.database import get_db
from app.db.models import ScheduledPost, ContentDraft, ContentVariant
from app.publishing.services import PublishingService
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_platform_credentials(platform: str, organization_id: Optional[int] = None) -> Dict[str, Any]:
    """
    Pobiera dane uwierzytelniające dla danej platformy
    
    Args:
        platform: Nazwa platformy (linkedin, facebook, instagram, wordpress)
        organization_id: ID organizacji (opcjonalne)
        
    Returns:
        Dict zawierający dane uwierzytelniające
    """
    # TODO: Implementacja pobierania danych uwierzytelniających
    # Na razie zwracamy placeholder - w przyszłości będzie to pobierać z:
    # - zmiennych środowiskowych
    # - serwisu zarządzania konfiguracją
    # - bazy danych z zaszyfrowanymi tokenami
    
    credentials = {
        "linkedin": {
            "access_token": settings.LINKEDIN_ACCESS_TOKEN if hasattr(settings, 'LINKEDIN_ACCESS_TOKEN') else "placeholder_linkedin_token",
            "client_id": settings.LINKEDIN_CLIENT_ID if hasattr(settings, 'LINKEDIN_CLIENT_ID') else "placeholder_client_id",
        },
        "facebook": {
            "access_token": settings.FACEBOOK_ACCESS_TOKEN if hasattr(settings, 'FACEBOOK_ACCESS_TOKEN') else "placeholder_facebook_token",
            "page_id": settings.FACEBOOK_PAGE_ID if hasattr(settings, 'FACEBOOK_PAGE_ID') else "placeholder_page_id",
        },
        "instagram": {
            "access_token": settings.INSTAGRAM_ACCESS_TOKEN if hasattr(settings, 'INSTAGRAM_ACCESS_TOKEN') else "placeholder_instagram_token",
            "account_id": settings.INSTAGRAM_ACCOUNT_ID if hasattr(settings, 'INSTAGRAM_ACCOUNT_ID') else "placeholder_account_id",
        },
        "wordpress": {
            "username": settings.WORDPRESS_USERNAME if hasattr(settings, 'WORDPRESS_USERNAME') else "placeholder_username",
            "password": settings.WORDPRESS_PASSWORD if hasattr(settings, 'WORDPRESS_PASSWORD') else "placeholder_password",
            "site_url": settings.WORDPRESS_SITE_URL if hasattr(settings, 'WORDPRESS_SITE_URL') else "https://example.com",
        }
    }
    
    return credentials.get(platform.lower(), {})


@celery_app.task(name="publish_post_task")
def publish_post_task(scheduled_post_id: int) -> Dict[str, Any]:
    """
    Zadanie Celery do publikacji pojedynczego posta
    
    Args:
        scheduled_post_id: ID zaplanowanego posta do publikacji
        
    Returns:
        Dict z rezultatem operacji
    """
    db = next(get_db())
    publishing_service = PublishingService()
    
    try:
        # Pobierz zaplanowany post wraz z powiązanym ContentVariant
        scheduled_post = db.query(ScheduledPost).filter(
            ScheduledPost.id == scheduled_post_id
        ).first()
        
        if not scheduled_post:
            logger.error(f"ScheduledPost with id {scheduled_post_id} not found")
            return {"success": False, "error": "Scheduled post not found"}
        
        # Pobierz zaakceptowany content variant
        content_variant = db.query(ContentVariant).filter(
            ContentVariant.id == scheduled_post.content_variant_id,
            ContentVariant.status == "approved",
            ContentVariant.is_active == True
        ).first()
        
        if not content_variant:
            logger.error(f"No approved content variant found for scheduled post {scheduled_post_id}")
            scheduled_post.status = "failed"
            db.commit()
            return {"success": False, "error": "No approved content variant found"}
        
        # Pobierz dane uwierzytelniające
        credentials = get_platform_credentials(
            content_variant.platform_name, 
            # organization_id można pobrać z scheduled_post jeśli będzie potrzebne
        )
        
        if not credentials:
            logger.error(f"No credentials found for platform {content_variant.platform_name}")
            scheduled_post.status = "failed"
            db.commit()
            return {"success": False, "error": f"No credentials for platform {content_variant.platform_name}"}
        
        # Przygotuj dane do publikacji
        content_data = {
            "content": content_variant.content_text,
            "title": scheduled_post.title,
            "caption": content_variant.content_text,  # For Instagram
            "image_url": "",  # TODO: Obsługa obrazków
        }
        
        # Publikuj na platformie
        logger.info(f"Publishing post {scheduled_post_id} to {content_variant.platform_name}")
        
        # Używamy synchronicznej wersji metody (w kontekście Celery task)
        import asyncio
        
        async def publish_async():
            return await publishing_service.publish_to_platform(
                content_variant.platform_name, 
                content_data, 
                credentials
            )
        
        # Uruchom zadanie asynchroniczne
        success = asyncio.run(publish_async())
        
        # Zaktualizuj status w bazie danych
        if success:
            scheduled_post.status = "published"
            logger.info(f"Successfully published post {scheduled_post_id} to {content_variant.platform_name}")
        else:
            scheduled_post.status = "failed"
            logger.error(f"Failed to publish post {scheduled_post_id} to {content_variant.platform_name}")
        
        db.commit()
        
        return {
            "success": success,
            "scheduled_post_id": scheduled_post_id,
            "platform": content_variant.platform_name,
            "status": scheduled_post.status
        }
        
    except Exception as e:
        logger.error(f"Error publishing post {scheduled_post_id}: {str(e)}")
        
        # Zaktualizuj status na failed
        try:
            scheduled_post = db.query(ScheduledPost).filter(
                ScheduledPost.id == scheduled_post_id
            ).first()
            if scheduled_post:
                scheduled_post.status = "failed"
                db.commit()
        except Exception as db_error:
            logger.error(f"Error updating post status: {str(db_error)}")
        
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="schedule_due_posts_task")
def schedule_due_posts_task() -> Dict[str, Any]:
    """
    Zadanie cykliczne do planowania postów, które mają być opublikowane
    w najbliższym czasie
    
    Returns:
        Dict z rezultatem operacji
    """
    db = next(get_db())
    
    try:
        # Znajdź posty do zaplanowania (w ciągu następnych 30 minut)
        now = datetime.utcnow()
        future_time = now + timedelta(minutes=30)
        
        scheduled_posts = db.query(ScheduledPost).filter(
            ScheduledPost.status == "scheduled",
            ScheduledPost.publication_date >= now,
            ScheduledPost.publication_date <= future_time
        ).all()
        
        scheduled_count = 0
        failed_count = 0
        
        for post in scheduled_posts:
            try:
                # Sprawdź czy istnieje zaakceptowany content variant
                content_variant = db.query(ContentVariant).filter(
                    ContentVariant.id == post.content_variant_id,
                    ContentVariant.status == "approved",
                    ContentVariant.is_active == True
                ).first()
                
                if not content_variant:
                    logger.warning(f"Skipping post {post.id} - no approved content variant")
                    continue
                
                # Zaplanuj zadanie publikacji z dokładnym czasem
                publish_post_task.apply_async(
                    args=[post.id],
                    eta=post.publication_date
                )
                
                # Zaktualizuj status na queued
                post.status = "queued"
                scheduled_count += 1
                
                logger.info(f"Scheduled post {post.id} for publication at {post.publication_date}")
                
            except Exception as e:
                logger.error(f"Error scheduling post {post.id}: {str(e)}")
                failed_count += 1
        
        db.commit()
        
        result = {
            "success": True,
            "scheduled_count": scheduled_count,
            "failed_count": failed_count,
            "total_posts_checked": len(scheduled_posts)
        }
        
        logger.info(f"Scheduled {scheduled_count} posts, {failed_count} failed")
        return result
        
    except Exception as e:
        logger.error(f"Error in schedule_due_posts_task: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="cleanup_old_posts_task")
def cleanup_old_posts_task() -> Dict[str, Any]:
    """
    Zadanie cykliczne do czyszczenia starych postów
    
    Returns:
        Dict z rezultatem operacji
    """
    db = next(get_db())
    
    try:
        # Znajdź posty starsze niż 30 dni ze statusem failed lub published
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        
        old_posts = db.query(ScheduledPost).filter(
            ScheduledPost.status.in_(["failed", "published"]),
            ScheduledPost.updated_at < cutoff_date
        ).all()
        
        # Opcjonalnie: archiwizuj lub usuń stare posty
        # Na razie tylko logujemy
        logger.info(f"Found {len(old_posts)} old posts for potential cleanup")
        
        return {
            "success": True,
            "old_posts_count": len(old_posts),
            "action": "logged_only"
        }
        
    except Exception as e:
        logger.error(f"Error in cleanup_old_posts_task: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close()


@celery_app.task(name="monitor_publishing_status_task")
def monitor_publishing_status_task() -> Dict[str, Any]:
    """
    Zadanie do monitorowania statusów publikacji i logowania statystyk
    
    Returns:
        Dict z rezultatem operacji
    """
    db = next(get_db())
    
    try:
        # Zbierz statystyki publikacji
        stats = {
            "scheduled": db.query(ScheduledPost).filter(ScheduledPost.status == "scheduled").count(),
            "queued": db.query(ScheduledPost).filter(ScheduledPost.status == "queued").count(),
            "published": db.query(ScheduledPost).filter(ScheduledPost.status == "published").count(),
            "failed": db.query(ScheduledPost).filter(ScheduledPost.status == "failed").count(),
        }
        
        # Sprawdź zadania, które mogły "utknąć" w statusie queued
        stuck_threshold = datetime.utcnow() - timedelta(hours=2)
        stuck_posts = db.query(ScheduledPost).filter(
            ScheduledPost.status == "queued",
            ScheduledPost.updated_at < stuck_threshold
        ).all()
        
        # Opcjonalnie: zresetuj "utknięte" posty do statusu scheduled
        for post in stuck_posts:
            if post.publication_date > datetime.utcnow():
                post.status = "scheduled"
                logger.warning(f"Reset stuck post {post.id} from queued to scheduled")
        
        if stuck_posts:
            db.commit()
        
        logger.info(f"Publishing stats: {stats}, stuck posts reset: {len(stuck_posts)}")
        
        return {
            "success": True,
            "stats": stats,
            "stuck_posts_reset": len(stuck_posts)
        }
        
    except Exception as e:
        logger.error(f"Error in monitor_publishing_status_task: {str(e)}")
        return {"success": False, "error": str(e)}
    
    finally:
        db.close() 