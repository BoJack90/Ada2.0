from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.tasks.example_tasks import test_celery_task
import redis
from app.core.config import settings

router = APIRouter()

@router.get("/health")
async def health_check():
    """Sprawdzenie stanu aplikacji"""
    return {
        "status": "healthy",
        "message": "Ada 2.0 działa poprawnie!"
    }

@router.get("/health/db")
async def health_check_db(db: Session = Depends(get_db)):
    """Sprawdzenie połączenia z bazą danych"""
    try:
        # Próba wykonania prostego zapytania
        db.execute("SELECT 1")
        return {
            "status": "healthy",
            "service": "database",
            "message": "Połączenie z PostgreSQL działa"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "database",
            "message": f"Błąd połączenia z bazą: {str(e)}"
        }

@router.get("/health/redis")
async def health_check_redis():
    """Sprawdzenie połączenia z Redis"""
    try:
        r = redis.from_url(settings.redis_url)
        r.ping()
        return {
            "status": "healthy",
            "service": "redis",
            "message": "Połączenie z Redis działa"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "redis",
            "message": f"Błąd połączenia z Redis: {str(e)}"
        }

@router.post("/health/celery")
async def health_check_celery():
    """Sprawdzenie działania Celery"""
    try:
        # Uruchomienie testowego zadania
        task = test_celery_task.delay("health_check")
        return {
            "status": "healthy",
            "service": "celery",
            "message": "Zadanie Celery zostało uruchomione",
            "task_id": task.id
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "service": "celery",
            "message": f"Błąd Celery: {str(e)}"
        }
