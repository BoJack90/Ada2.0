from typing import Dict, Any
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, Path, Query, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.strategy_parser import StrategyParser
from app.core.file_validation import validate_upload
from app.core.rate_limit import limiter


router = APIRouter(prefix="/api/v1", tags=["Strategy Analysis"])


@router.post("/clients/{client_id}/strategy", response_model=Dict[str, Any])
@limiter.limit("10/minute")
async def upload_strategy_file(
    request: Request,
    client_id: int = Path(..., description="ID organizacji/klienta"),
    file: UploadFile = File(..., description="Plik strategii do analizy"),
    created_by_id: int = Query(1, description="ID użytkownika tworzącego strategię"),
    db: Session = Depends(get_db)
):
    """
    Endpoint do przesyłania pliku strategii komunikacji do analizy przez AI.
    
    Proces:
    1. Waliduje przesłany plik
    2. Uruchamia zadanie Celery w tle
    3. Zwraca task_id do sprawdzania statusu
    
    Args:
        client_id: ID organizacji/klienta
        file: Plik do analizy (PDF, DOC, DOCX, TXT, HTML, RTF)
        created_by_id: ID użytkownika tworzącego strategię
        
    Returns:
        202 Accepted z task_id i informacjami o pliku
        
    Raises:
        400: Nieprawidłowy plik
        500: Błąd serwera
    """
    
    try:
        # Walidacja client_id
        if client_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid client_id. Must be a positive integer."
            )
        
        # Sprawdzenie czy organizacja istnieje (opcjonalne)
        # TODO: Dodać walidację istnienia organizacji w bazie danych
        
        # Walidacja przesłanego pliku
        validate_upload(file, file_type="document")
        
        # Tworzenie instancji strategy_parser
        strategy_parser = StrategyParser(db)
        
        # Uruchomienie analizy pliku
        result = await strategy_parser.parse_strategy_file(
            organization_id=client_id,
            file=file,
            created_by_id=created_by_id
        )
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/clients/{client_id}/strategy/task/{task_id}", response_model=Dict[str, Any])
async def get_task_status(
    client_id: int = Path(..., description="ID organizacji/klienta"),
    task_id: str = Path(..., description="ID zadania do sprawdzenia"),
    db: Session = Depends(get_db)
):
    """
    Endpoint do sprawdzania statusu zadania analizy strategii.
    
    Args:
        client_id: ID organizacji/klienta
        task_id: ID zadania Celery
        
    Returns:
        Status zadania z informacjami o postępie
    """
    
    try:
        # Walidacja client_id
        if client_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid client_id. Must be a positive integer."
            )
        
        # Tworzenie instancji strategy_parser
        strategy_parser = StrategyParser(db)
        
        # Pobieranie statusu zadania
        status = strategy_parser.get_task_status(task_id)
        
        # Dodanie client_id do odpowiedzi
        status['client_id'] = client_id
        
        return status
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get task status: {str(e)}"
        )


@router.get("/clients/{client_id}/strategies", response_model=Dict[str, Any])
async def list_strategies(
    client_id: int = Path(..., description="ID organizacji/klienta"),
    db: Session = Depends(get_db)
):
    """
    Endpoint do pobierania listy strategii komunikacji dla organizacji.
    
    Args:
        client_id: ID organizacji/klienta
        
    Returns:
        Lista strategii komunikacji dla organizacji
    """
    
    try:
        # Walidacja client_id
        if client_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid client_id. Must be a positive integer."
            )
        
        # Tworzenie instancji strategy_parser
        strategy_parser = StrategyParser(db)
        
        # Pobieranie listy strategii
        strategies = strategy_parser.list_organization_strategies(client_id)
        
        return strategies
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve strategies: {str(e)}"
        )


@router.get("/clients/{client_id}/strategy/{strategy_id}", response_model=Dict[str, Any])
async def get_strategy_details(
    client_id: int = Path(..., description="ID organizacji/klienta"),
    strategy_id: int = Path(..., description="ID strategii"),
    db: Session = Depends(get_db)
):
    """
    Endpoint do pobierania szczegółów konkretnej strategii komunikacji.
    
    Args:
        client_id: ID organizacji/klienta
        strategy_id: ID strategii
        
    Returns:
        Szczegółowe informacje o strategii z wszystkimi powiązanymi danymi
    """
    
    try:
        from app.db.models import (
            CommunicationStrategy, Persona, PlatformStyle, CTARule, GeneralStyle,
            CommunicationGoal, ForbiddenPhrase, PreferredPhrase, SampleContentType
        )
        
        # Walidacja parametrów
        if client_id <= 0 or strategy_id <= 0:
            raise HTTPException(
                status_code=400,
                detail="Invalid client_id or strategy_id. Must be positive integers."
            )
        
        # Pobieranie głównej strategii
        strategy = db.query(CommunicationStrategy)\
            .filter(CommunicationStrategy.id == strategy_id)\
            .filter(CommunicationStrategy.organization_id == client_id)\
            .filter(CommunicationStrategy.is_active == True)\
            .first()
        
        if not strategy:
            raise HTTPException(
                status_code=404,
                detail="Strategy not found or not accessible"
            )
        
        # Pobieranie powiązanych danych
        communication_goals = db.query(CommunicationGoal)\
            .filter(CommunicationGoal.communication_strategy_id == strategy_id)\
            .all()
        
        personas = db.query(Persona)\
            .filter(Persona.communication_strategy_id == strategy_id)\
            .all()
        
        general_style = db.query(GeneralStyle)\
            .filter(GeneralStyle.communication_strategy_id == strategy_id)\
            .first()
        
        platform_styles = db.query(PlatformStyle)\
            .filter(PlatformStyle.communication_strategy_id == strategy_id)\
            .all()
        
        forbidden_phrases = db.query(ForbiddenPhrase)\
            .filter(ForbiddenPhrase.communication_strategy_id == strategy_id)\
            .all()
        
        preferred_phrases = db.query(PreferredPhrase)\
            .filter(PreferredPhrase.communication_strategy_id == strategy_id)\
            .all()
        
        cta_rules = db.query(CTARule)\
            .filter(CTARule.communication_strategy_id == strategy_id)\
            .all()
        
        sample_content_types = db.query(SampleContentType)\
            .filter(SampleContentType.communication_strategy_id == strategy_id)\
            .all()
        
        # Składanie odpowiedzi
        result = {
            'id': strategy.id,
            'name': strategy.name,
            'description': strategy.description,
            'organization_id': strategy.organization_id,
            'created_by_id': strategy.created_by_id,
            'is_active': strategy.is_active,
            'created_at': strategy.created_at.isoformat(),
            'updated_at': strategy.updated_at.isoformat(),
            'communication_goals': [goal.goal_text for goal in communication_goals],
            'target_audiences': [
                {
                    'id': persona.id,
                    'name': persona.name,
                    'description': persona.description
                } for persona in personas
            ],
            'general_style': {
                'language': general_style.language,
                'tone': general_style.tone,
                'technical_content': general_style.technical_content,
                'employer_branding_content': general_style.employer_branding_content
            } if general_style else None,
            'platform_styles': [
                {
                    'id': ps.id,
                    'platform_name': ps.platform_name,
                    'length_description': ps.length_description,
                    'style_description': ps.style_description,
                    'notes': ps.notes
                } for ps in platform_styles
            ],
            'forbidden_phrases': [fp.phrase for fp in forbidden_phrases],
            'preferred_phrases': [pp.phrase for pp in preferred_phrases],
            'cta_rules': [
                {
                    'id': cta.id,
                    'content_type': cta.content_type,
                    'cta_text': cta.cta_text
                } for cta in cta_rules
            ],
            'sample_content_types': [sct.content_type for sct in sample_content_types]
        }
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve strategy details: {str(e)}"
        ) 