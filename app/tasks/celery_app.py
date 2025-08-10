from celery import Celery
from app.core.config import settings
from app.publishing.beat_schedule import CELERY_BEAT_SCHEDULE, CELERY_TIMEZONE

# Create Celery instance
celery_app = Celery(
    "ada_worker",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.example_tasks", "app.tasks.content_generation", "app.tasks.main_flow", "app.tasks.content_draft", "app.tasks.variant_generation", "app.tasks.brief_analysis", "app.tasks.website_analysis", "app.publishing.tasks"]
)

# Configure Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone=CELERY_TIMEZONE,
    enable_utc=True,
    result_expires=3600,  # 1 hour
    beat_schedule=CELERY_BEAT_SCHEDULE,
    # Removed django_celery_beat scheduler - using default PersistentScheduler for FastAPI
)
