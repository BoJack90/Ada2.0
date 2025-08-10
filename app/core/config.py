from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Konfiguracja aplikacji"""
    
    # Database
    database_url: str = "postgresql://ada_user:ada_password@db:5432/ada_db"
    
    # Redis
    redis_url: str = "redis://redis:6379/0"
    
    # Celery
    celery_broker_url: str = "redis://redis:6379/0"
    celery_result_backend: str = "redis://redis:6379/0"
    
    # Security
    secret_key: str = "ada2.0-super-secret-key-change-in-production-2025"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440  # 24 hours
    
    # App settings
    app_name: str = "Ada 2.0"
    debug: bool = True
    
    # API Keys
    tavily_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    google_ai_api_key: Optional[str] = None
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000", 
        "http://localhost:8081", 
        "http://frontend:3000", 
        "http://host.docker.internal:8081"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()
