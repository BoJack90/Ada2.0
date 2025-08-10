import base64
from typing import Dict, Any, Optional
from fastapi import UploadFile, HTTPException
from sqlalchemy.orm import Session

from app.tasks.content_generation import process_strategy_file_task
from app.db.database import get_db


class StrategyParser:
    """
    Serwis do analizy plików strategii komunikacji przez AI.
    Obsługuje upload plików i uruchamianie zadań w tle.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    async def parse_strategy_file(
        self, 
        organization_id: int,
        file: UploadFile,
        created_by_id: int = 1
    ) -> Dict[str, Any]:
        """
        Analizuje plik strategii komunikacji i uruchamia zadanie w tle.
        
        Args:
            organization_id: ID organizacji
            file: Przesłany plik
            created_by_id: ID użytkownika tworzącego strategię
            
        Returns:
            dict: Informacje o uruchomionym zadaniu
            
        Raises:
            HTTPException: W przypadku nieprawidłowego pliku lub błędu
        """
        
        try:
            # Walidacja pliku
            if not file.filename:
                raise HTTPException(
                    status_code=400,
                    detail="No file provided"
                )
            
            # Sprawdzanie typu pliku
            allowed_mime_types = [
                'text/plain',
                'application/pdf',
                'application/msword',
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'text/html',
                'application/rtf'
            ]
            
            if file.content_type not in allowed_mime_types:
                raise HTTPException(
                    status_code=400,
                    detail=f"Unsupported file type: {file.content_type}. "
                           f"Supported types: {', '.join(allowed_mime_types)}"
                )
            
            # Sprawdzanie rozmiaru pliku (maksymalnie 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            file_content = await file.read()
            
            if len(file_content) > max_size:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size is {max_size / (1024*1024):.1f}MB"
                )
            
            # Sprawdzanie czy plik nie jest pusty
            if len(file_content) == 0:
                raise HTTPException(
                    status_code=400,
                    detail="File is empty"
                )
            
            # Kodowanie zawartości pliku do base64
            file_content_b64 = base64.b64encode(file_content).decode('utf-8')
            
            # Uruchomienie zadania w tle
            task = process_strategy_file_task.delay(
                organization_id=organization_id,
                file_content_b64=file_content_b64,
                file_mime_type=file.content_type,
                created_by_id=created_by_id
            )
            
            return {
                'task_id': task.id,
                'status': 'PENDING',
                'message': 'File upload successful. Processing started.',
                'file_name': file.filename,
                'file_size': len(file_content),
                'file_type': file.content_type,
                'organization_id': organization_id
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Internal server error: {str(e)}"
            )
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """
        Pobiera status zadania Celery.
        
        Args:
            task_id: ID zadania
            
        Returns:
            dict: Status zadania
        """
        
        try:
            from app.tasks.celery_app import celery_app
            
            # Pobieranie stanu zadania
            task_result = celery_app.AsyncResult(task_id)
            
            if task_result.state == 'PENDING':
                return {
                    'task_id': task_id,
                    'status': 'PENDING',
                    'message': 'Task is waiting to be processed'
                }
            elif task_result.state == 'PROGRESS':
                return {
                    'task_id': task_id,
                    'status': 'PROGRESS',
                    'current': task_result.info.get('current', 0),
                    'total': task_result.info.get('total', 1),
                    'message': task_result.info.get('status', 'Processing...')
                }
            elif task_result.state == 'SUCCESS':
                return {
                    'task_id': task_id,
                    'status': 'SUCCESS',
                    'result': task_result.result
                }
            elif task_result.state == 'FAILURE':
                return {
                    'task_id': task_id,
                    'status': 'FAILURE',
                    'error': str(task_result.info)
                }
            else:
                return {
                    'task_id': task_id,
                    'status': task_result.state,
                    'message': f'Task is in state: {task_result.state}'
                }
                
        except Exception as e:
            return {
                'task_id': task_id,
                'status': 'ERROR',
                'error': f'Failed to get task status: {str(e)}'
            }
    
    def list_organization_strategies(self, organization_id: int) -> Dict[str, Any]:
        """
        Pobiera listę strategii komunikacji dla organizacji.
        
        Args:
            organization_id: ID organizacji
            
        Returns:
            dict: Lista strategii
        """
        
        try:
            from app.db.models import CommunicationStrategy
            
            # Pobieranie strategii z bazy danych
            strategies = self.db.query(CommunicationStrategy)\
                .filter(CommunicationStrategy.organization_id == organization_id)\
                .filter(CommunicationStrategy.is_active == True)\
                .order_by(CommunicationStrategy.created_at.desc())\
                .all()
            
            strategies_list = []
            for strategy in strategies:
                strategies_list.append({
                    'id': strategy.id,
                    'name': strategy.name,
                    'description': strategy.description,
                    'created_at': strategy.created_at.isoformat(),
                    'updated_at': strategy.updated_at.isoformat(),
                    'created_by_id': strategy.created_by_id
                })
            
            return {
                'organization_id': organization_id,
                'strategies': strategies_list,
                'total_count': len(strategies_list)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to retrieve strategies: {str(e)}"
            )


# Dependency provider dla FastAPI
def get_strategy_parser(db: Session = None) -> StrategyParser:
    """
    Tworzy i zwraca instancję StrategyParser.
    Używane jako dependency w FastAPI endpointach.
    """
    if db is None:
        from app.db.database import SessionLocal
        db = SessionLocal()
    
    return StrategyParser(db) 