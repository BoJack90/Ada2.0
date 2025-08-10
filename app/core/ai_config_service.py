from functools import lru_cache
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import AIModelAssignment, OrganizationAIModelAssignment


class AIConfigService:
    """
    Zarządza konfiguracją modeli AI z mechanizmem cache'owania.
    Obsługuje zarówno konfiguracje globalne jak i specyficzne dla organizacji.
    """
    
    def __init__(self, db_session: Session, organization_id: Optional[int] = None):
        self.db_session = db_session
        self.organization_id = organization_id
    
    async def get_model_for_task(self, task_name: str) -> Optional[str]:
        """
        Pobiera nazwę modelu AI przypisaną do danego zadania z bazy danych.
        Najpierw szuka konfiguracji specyficznej dla organizacji, potem globalnej.
        
        Args:
            task_name: Nazwa zadania (np. 'strategy_parser')
            
        Returns:
            Nazwa modelu jako string lub None jeśli nie znaleziono
        """
        try:
            # Jeśli podano organization_id, najpierw szukaj konfiguracji organizacji
            if self.organization_id:
                org_assignment = self.db_session.query(OrganizationAIModelAssignment)\
                    .filter(OrganizationAIModelAssignment.organization_id == self.organization_id)\
                    .filter(OrganizationAIModelAssignment.task_name == task_name)\
                    .filter(OrganizationAIModelAssignment.is_active == True)\
                    .first()
                
                if org_assignment:
                    return org_assignment.model_name
            
            # Jeśli nie znaleziono konfiguracji organizacji, użyj globalnej
            result = self.db_session.query(AIModelAssignment)\
                .filter(AIModelAssignment.task_name == task_name)\
                .first()
            
            if result:
                return result.model_name
            return None
            
        except Exception as e:
            print(f"Błąd podczas pobierania modelu dla zadania {task_name}: {str(e)}")
            return None
    
    def _get_cached_model(self, task_name: str) -> Optional[str]:
        """
        Cache'owana wersja get_model_for_task dla lepszej wydajności.
        Uwaga: Cache jest per instancja, więc różne organizacje mają osobne cache.
        """
        try:
            # Jeśli podano organization_id, najpierw szukaj konfiguracji organizacji
            if self.organization_id:
                org_assignment = self.db_session.query(OrganizationAIModelAssignment)\
                    .filter(OrganizationAIModelAssignment.organization_id == self.organization_id)\
                    .filter(OrganizationAIModelAssignment.task_name == task_name)\
                    .filter(OrganizationAIModelAssignment.is_active == True)\
                    .first()
                
                if org_assignment:
                    return org_assignment.model_name
            
            # Jeśli nie znaleziono konfiguracji organizacji, użyj globalnej
            result = self.db_session.query(AIModelAssignment)\
                .filter(AIModelAssignment.task_name == task_name)\
                .first()
            
            if result:
                return result.model_name
            return None
            
        except Exception as e:
            print(f"Błąd podczas pobierania modelu z cache dla zadania {task_name}: {str(e)}")
            return None
    
    def clear_cache(self):
        """Czyści cache przypisań modeli."""
        # Z powodu zmiany implementacji, cache jest teraz per-instancja
        pass
    
    async def update_model_assignment(self, task_name: str, model_name: str) -> bool:
        """
        Aktualizuje przypisanie modelu do zadania.
        Jeśli organization_id jest ustawione, tworzy/aktualizuje przypisanie organizacji.
        
        Args:
            task_name: Nazwa zadania
            model_name: Nazwa nowego modelu
            
        Returns:
            True jeśli aktualizacja się powiodła, False w przeciwnym razie
        """
        try:
            if self.organization_id:
                # Zarządzaj przypisaniem dla organizacji
                existing = self.db_session.query(OrganizationAIModelAssignment)\
                    .filter(OrganizationAIModelAssignment.organization_id == self.organization_id)\
                    .filter(OrganizationAIModelAssignment.task_name == task_name)\
                    .first()
                
                if existing:
                    existing.model_name = model_name
                    existing.is_active = True
                else:
                    # Znajdź base assignment jeśli istnieje
                    base_assignment = self.db_session.query(AIModelAssignment)\
                        .filter(AIModelAssignment.task_name == task_name)\
                        .first()
                    
                    new_assignment = OrganizationAIModelAssignment(
                        organization_id=self.organization_id,
                        task_name=task_name,
                        model_name=model_name,
                        base_assignment_id=base_assignment.id if base_assignment else None,
                        is_active=True
                    )
                    self.db_session.add(new_assignment)
            else:
                # Zarządzaj globalnym przypisaniem
                existing = self.db_session.query(AIModelAssignment)\
                    .filter(AIModelAssignment.task_name == task_name)\
                    .first()
                
                if existing:
                    existing.model_name = model_name
                else:
                    new_assignment = AIModelAssignment(
                        task_name=task_name,
                        model_name=model_name
                    )
                    self.db_session.add(new_assignment)
            
            self.db_session.commit()
            return True
            
        except Exception as e:
            print(f"Błąd podczas aktualizacji przypisania modelu {task_name}: {str(e)}")
            self.db_session.rollback()
            return False
    
    async def get_all_assignments(self) -> list:
        """
        Pobiera wszystkie przypisania modeli.
        Dla organizacji zwraca połączenie przypisań organizacji i globalnych.
        """
        try:
            assignments = {}
            
            # Najpierw pobierz globalne przypisania
            global_assignments = self.db_session.query(AIModelAssignment).all()
            for assignment in global_assignments:
                assignments[assignment.task_name] = {
                    'model_name': assignment.model_name,
                    'is_custom': False,
                    'description': assignment.description
                }
            
            # Jeśli mamy organization_id, nadpisz przypisaniami organizacji
            if self.organization_id:
                org_assignments = self.db_session.query(OrganizationAIModelAssignment)\
                    .filter(OrganizationAIModelAssignment.organization_id == self.organization_id)\
                    .filter(OrganizationAIModelAssignment.is_active == True)\
                    .all()
                
                for assignment in org_assignments:
                    assignments[assignment.task_name] = {
                        'model_name': assignment.model_name,
                        'is_custom': True,
                        'description': None  # Można dodać opis do modelu organizacji
                    }
            
            return [
                {
                    'task_name': task_name,
                    'model_name': data['model_name'],
                    'is_custom': data['is_custom'],
                    'description': data['description']
                }
                for task_name, data in assignments.items()
            ]
            
        except Exception as e:
            print(f"Błąd podczas pobierania wszystkich przypisań: {str(e)}")
            return []


# Dependency provider dla FastAPI
def get_ai_config_service(db: Session = None, organization_id: Optional[int] = None) -> AIConfigService:
    """
    Tworzy i zwraca instancję AIConfigService.
    Używane jako dependency w FastAPI endpointach.
    
    Args:
        db: Sesja bazy danych
        organization_id: ID organizacji (opcjonalne)
    """
    if db is None:
        # Fallback - jeśli nie podano sesji, utworzy nową
        from app.db.database import SessionLocal
        db = SessionLocal()
    
    return AIConfigService(db_session=db, organization_id=organization_id)