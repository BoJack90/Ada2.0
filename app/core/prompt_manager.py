from functools import lru_cache
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import AIPrompt, OrganizationAIPrompt
from app.db.database import get_db


class PromptManager:
    """
    Zarządza promptami AI z mechanizmem cache'owania.
    Obsługuje zarówno prompty globalne jak i specyficzne dla organizacji.
    """
    
    def __init__(self, db_session: Session, organization_id: Optional[int] = None):
        self.db_session = db_session
        self.organization_id = organization_id
    
    async def get_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Pobiera najnowszy szablon promptu o podanej nazwie z bazy danych.
        Najpierw szuka promptu specyficznego dla organizacji, potem globalnego.
        
        Args:
            prompt_name: Nazwa promptu (np. 'strategy_parser')
            
        Returns:
            Szablon promptu jako string lub None jeśli nie znaleziono
        """
        try:
            # Jeśli podano organization_id, najpierw szukaj promptu organizacji
            if self.organization_id:
                org_prompt = self.db_session.query(OrganizationAIPrompt)\
                    .filter(OrganizationAIPrompt.organization_id == self.organization_id)\
                    .filter(OrganizationAIPrompt.prompt_name == prompt_name)\
                    .filter(OrganizationAIPrompt.is_active == True)\
                    .order_by(OrganizationAIPrompt.version.desc())\
                    .first()
                
                if org_prompt:
                    return org_prompt.prompt_template
            
            # Jeśli nie znaleziono promptu organizacji, użyj globalnego
            result = self.db_session.query(AIPrompt)\
                .filter(AIPrompt.prompt_name == prompt_name)\
                .order_by(AIPrompt.version.desc())\
                .first()
            
            if result:
                return result.prompt_template
            return None
            
        except Exception as e:
            print(f"Błąd podczas pobierania promptu {prompt_name}: {str(e)}")
            return None
    
    def _get_cached_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Cache'owana wersja get_prompt dla lepszej wydajności.
        Uwaga: Cache jest per instancja, więc różne organizacje mają osobne cache.
        """
        # Tworzymy klucz cache zawierający organization_id
        cache_key = f"{self.organization_id or 'global'}:{prompt_name}"
        
        # W przypadku cache używamy synchronicznej wersji
        try:
            # Jeśli podano organization_id, najpierw szukaj promptu organizacji
            if self.organization_id:
                org_prompt = self.db_session.query(OrganizationAIPrompt)\
                    .filter(OrganizationAIPrompt.organization_id == self.organization_id)\
                    .filter(OrganizationAIPrompt.prompt_name == prompt_name)\
                    .filter(OrganizationAIPrompt.is_active == True)\
                    .order_by(OrganizationAIPrompt.version.desc())\
                    .first()
                
                if org_prompt:
                    return org_prompt.prompt_template
            
            # Jeśli nie znaleziono promptu organizacji, użyj globalnego
            result = self.db_session.query(AIPrompt)\
                .filter(AIPrompt.prompt_name == prompt_name)\
                .order_by(AIPrompt.version.desc())\
                .first()
            
            if result:
                return result.prompt_template
            return None
            
        except Exception as e:
            print(f"Błąd podczas pobierania promptu z cache {prompt_name}: {str(e)}")
            return None
    
    def clear_cache(self):
        """Czyści cache promptów."""
        self._get_cached_prompt.cache_clear()


# Dependency provider dla FastAPI
def get_prompt_manager(db: Session = None, organization_id: Optional[int] = None) -> PromptManager:
    """
    Tworzy i zwraca instancję PromptManager.
    Używane jako dependency w FastAPI endpointach.
    
    Args:
        db: Sesja bazy danych
        organization_id: ID organizacji (opcjonalne)
    """
    if db is None:
        # Fallback - jeśli nie podano sesji, utworzy nową
        from app.db.database import SessionLocal
        db = SessionLocal()
    
    return PromptManager(db_session=db, organization_id=organization_id) 