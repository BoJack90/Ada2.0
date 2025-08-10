import base64
import json
import io
from typing import Dict, Any, Optional
from datetime import datetime
from celery import Celery
from sqlalchemy.orm import Session

from .celery_app import celery_app
from app.db.database import SessionLocal
from app.db.models import (
    CommunicationStrategy, Persona, PlatformStyle, CTARule, GeneralStyle,
    CommunicationGoal, ForbiddenPhrase, PreferredPhrase, SampleContentType
)
from app.db.schemas import CommunicationStrategyCreate
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService
from app.core.dependencies import get_prompt_manager, get_ai_config_service

# Importy do parsowania plików
try:
    import PyPDF2
    from docx import Document
    from bs4 import BeautifulSoup
    FILE_PARSING_AVAILABLE = True
except ImportError:
    PyPDF2 = None
    Document = None
    BeautifulSoup = None
    FILE_PARSING_AVAILABLE = False

# Google AI SDK
try:
    import google.generativeai as genai
    import os
    GEMINI_API_AVAILABLE = True
except ImportError:
    genai = None
    GEMINI_API_AVAILABLE = False


@celery_app.task(bind=True)
def process_strategy_file_task(self, organization_id: int, file_content_b64: str, file_mime_type: str, created_by_id: int = 1):
    """
    Asynchroniczne zadanie do analizy pliku strategii komunikacji przez AI
    i zapisu wyników do znormalizowanej bazy danych.
    
    Args:
        organization_id: ID organizacji
        file_content_b64: Zawartość pliku zakodowana w base64
        file_mime_type: Typ MIME pliku
        created_by_id: ID użytkownika tworzącego strategię
    
    Returns:
        dict: Wynik przetwarzania z ID utworzonej strategii lub błędem
    """
    
    try:
        # Dekodowanie zawartości pliku i ekstrakcja tekstu
        file_content = _extract_text_from_file(file_content_b64, file_mime_type)
        
        if not file_content:
            return {
                'status': 'FAILED',
                'error': 'Failed to extract text from file',
                'task_id': self.request.id
            }
        
        # Aktualizacja stanu zadania
        self.update_state(
            state='PROGRESS',
            meta={'current': 1, 'total': 4, 'status': 'Analyzing file with AI...'}
        )
        
        # Analiza AI
        ai_result = _analyze_with_ai(file_content)
        
        if not ai_result:
            return {
                'status': 'FAILED',
                'error': 'AI analysis failed',
                'task_id': self.request.id
            }
        
        # Aktualizacja stanu zadania
        self.update_state(
            state='PROGRESS',
            meta={'current': 2, 'total': 4, 'status': 'Validating AI response...'}
        )
        
        # Walidacja i konwersja do obiektu Pydantic
        try:
            # Dodanie organization_id do danych AI przed walidacją
            ai_result['organization_id'] = organization_id
            strategy_data = CommunicationStrategyCreate(**ai_result)
        except Exception as e:
            return {
                'status': 'FAILED',
                'error': f'Data validation failed: {str(e)}',
                'task_id': self.request.id
            }
        
        # Aktualizacja stanu zadania  
        self.update_state(
            state='PROGRESS',
            meta={'current': 3, 'total': 4, 'status': 'Saving to database...'}
        )
        
        # Zapis do bazy danych
        strategy_id = _save_to_database(strategy_data, created_by_id)
        
        if not strategy_id:
            return {
                'status': 'FAILED',
                'error': 'Database save failed',
                'task_id': self.request.id
            }
        
        # Aktualizacja stanu zadania
        self.update_state(
            state='PROGRESS',
            meta={'current': 4, 'total': 4, 'status': 'Completed successfully'}
        )
        
        return {
            'status': 'SUCCESS',
            'strategy_id': strategy_id,
            'organization_id': organization_id,
            'task_id': self.request.id,
            'message': 'Communication strategy processed and saved successfully'
        }
        
    except Exception as e:
        return {
            'status': 'FAILED',
            'error': str(e),
            'task_id': self.request.id
        }


def _extract_text_from_file(file_content_b64: str, file_mime_type: str) -> Optional[str]:
    """
    Ekstraktuje tekst z pliku w zależności od typu MIME.
    
    Args:
        file_content_b64: Zawartość pliku zakodowana w base64
        file_mime_type: Typ MIME pliku
        
    Returns:
        str: Wyekstraktowany tekst lub None w przypadku błędu
    """
    
    print(f"DEBUG _extract_text_from_file: Starting with MIME type: {file_mime_type}")
    
    try:
        # Dekodowanie zawartości pliku z base64
        file_content_binary = base64.b64decode(file_content_b64)
        print(f"DEBUG _extract_text_from_file: Decoded {len(file_content_binary)} bytes")
        
        # Tekst zwykły
        if file_mime_type.startswith('text/'):
            try:
                return file_content_binary.decode('utf-8')
            except UnicodeDecodeError:
                # Próba z różnymi kodowaniami
                for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                    try:
                        return file_content_binary.decode(encoding)
                    except UnicodeDecodeError:
                        continue
                return None
        
        # PDF
        elif file_mime_type == 'application/pdf':
            print(f"DEBUG _extract_text_from_file: Processing PDF")
            print(f"DEBUG _extract_text_from_file: FILE_PARSING_AVAILABLE={FILE_PARSING_AVAILABLE}, PyPDF2={PyPDF2}")
            
            if not FILE_PARSING_AVAILABLE or not PyPDF2:
                print("DEBUG _extract_text_from_file: PyPDF2 not available")
                return "PDF parsing not available. Please install PyPDF2."
            
            try:
                pdf_file = io.BytesIO(file_content_binary)
                pdf_reader = PyPDF2.PdfReader(pdf_file)
                print(f"DEBUG _extract_text_from_file: PDF has {len(pdf_reader.pages)} pages")
                
                text = ""
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    # Clean up excessive newlines from PDF extraction
                    page_text = ' '.join(page_text.split())
                    print(f"DEBUG _extract_text_from_file: Page {i+1} extracted {len(page_text)} characters")
                    text += page_text + "\n"
                
                print(f"DEBUG _extract_text_from_file: Total PDF text extracted: {len(text)} characters")
                return text.strip()
            except Exception as e:
                print(f"ERROR extracting text from PDF: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        # Word Document
        elif file_mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 
                                'application/msword']:
            if not FILE_PARSING_AVAILABLE or not Document:
                return "Word document parsing not available. Please install python-docx."
            
            try:
                doc_file = io.BytesIO(file_content_binary)
                doc = Document(doc_file)
                
                text = ""
                for paragraph in doc.paragraphs:
                    text += paragraph.text + "\n"
                
                return text.strip()
            except Exception as e:
                print(f"ERROR extracting text from Word document: {e}")
                return None
        
        # HTML
        elif file_mime_type == 'text/html':
            if not FILE_PARSING_AVAILABLE or not BeautifulSoup:
                return "HTML parsing not available. Please install beautifulsoup4."
            
            try:
                html_content = file_content_binary.decode('utf-8')
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Usuwanie tagów script i style
                for script in soup(["script", "style"]):
                    script.decompose()
                
                text = soup.get_text()
                
                # Czyszczenie tekstu
                lines = (line.strip() for line in text.splitlines())
                chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
                text = '\n'.join(chunk for chunk in chunks if chunk)
                
                return text
            except Exception as e:
                print(f"ERROR extracting text from HTML: {e}")
                return None
        
        # RTF (Rich Text Format)
        elif file_mime_type == 'application/rtf' or file_mime_type == 'text/rtf':
            try:
                # Podstawowa obsługa RTF - wyciągnięcie tekstu bez formatowania
                rtf_content = file_content_binary.decode('utf-8', errors='ignore')
                
                # Usuwanie podstawowych komend RTF
                import re
                text = re.sub(r'\\[a-z]+\d*', '', rtf_content)
                text = re.sub(r'[{}]', '', text)
                text = re.sub(r'\\', '', text)
                
                return text.strip()
            except Exception as e:
                print(f"ERROR extracting text from RTF: {e}")
                return None
        
        # Nieobsługiwany format
        else:
            return f"Unsupported file type: {file_mime_type}"
            
    except Exception as e:
        print(f"ERROR in _extract_text_from_file: {e}")
        return None


def _analyze_with_ai(file_content: str) -> Optional[Dict[str, Any]]:
    """
    Analizuje zawartość pliku za pomocą AI i zwraca wyniki w formacie JSON.
    
    Args:
        file_content: Zawartość pliku do analizy
        
    Returns:
        dict: Wyniki analizy AI lub None w przypadku błędu
    """
    
    try:
        # Tworzenie sesji bazy danych
        db = SessionLocal()
        
        try:
            # Pobieranie promptu z bazy danych (synchronicznie)
            prompt_manager = PromptManager(db)
            prompt_template = prompt_manager._get_cached_prompt('strategy_parser')
            
            if not prompt_template:
                print("ERROR: strategy_parser prompt not found in database")
                return None
            
            # Pobieranie konfiguracji modelu AI (synchronicznie)
            ai_config_service = AIConfigService(db)
            model_name = ai_config_service._get_cached_model('strategy_parser')
            
            if not model_name:
                print("ERROR: Model configuration for strategy_parser not found")
                return None
            
            # Generowanie JSON Schema dla promptu
            json_schema = _generate_json_schema()
            
            # Formatowanie promptu (używając replace zamiast format aby uniknąć konfliktów z JSON)
            formatted_prompt = prompt_template.replace('{json_schema}', json_schema)\
                                             .replace('{strategy_content}', file_content)
            
            # Wywołanie prawdziwego Gemini API
            print(f"DEBUG: Calling Gemini API with model: {model_name}")
            print(f"DEBUG: File content length: {len(file_content)}")
            ai_response = _call_gemini_api(formatted_prompt, model_name)
            
            # Parsowanie odpowiedzi AI
            if ai_response:
                print(f"DEBUG: AI Response received, length: {len(ai_response)}")
                print(f"DEBUG: AI Response (first 500 chars): {ai_response[:500]}")
                try:
                    parsed_response = json.loads(ai_response)
                    
                    # Obsługa null values dla głównych pól
                    if parsed_response.get('name') is None:
                        parsed_response['name'] = "Strategia komunikacji z analizy AI"
                    else:
                        # Ograniczenie długości nazwy do 190 znaków (bezpieczny margines)
                        parsed_response['name'] = str(parsed_response['name'])[:190]
                    
                    if parsed_response.get('description') is None:
                        parsed_response['description'] = "Strategia wygenerowana przez system AI"
                    
                    # Obsługa null values w general_style
                    if 'general_style' in parsed_response and parsed_response['general_style']:
                        general_style = parsed_response['general_style']
                        if general_style.get('language') is None:
                            general_style['language'] = "polski"
                        if general_style.get('tone') is None:
                            general_style['tone'] = "do ustalenia"
                        if general_style.get('technical_content') is None:
                            general_style['technical_content'] = "wymaga analizy"
                        if general_style.get('employer_branding_content') is None:
                            general_style['employer_branding_content'] = "wymaga analizy"
                    
                    print(f"SUCCESS: Gemini API analysis completed")
                    print(f"DEBUG: Parsed response keys: {list(parsed_response.keys())}")
                    print(f"DEBUG: Communication goals: {parsed_response.get('communication_goals', [])}")
                    print(f"DEBUG: Target audiences: {len(parsed_response.get('target_audiences', []))} audiences")
                    return parsed_response
                except json.JSONDecodeError as e:
                    print(f"ERROR: Failed to parse AI response as JSON: {e}")
                    print(f"Raw AI response: {ai_response[:500]}...")  # Pierwsze 500 znaków dla debug
            
            # Fallback - jeśli Gemini API nie działa, użyj analizy tekstu
            print("Using fallback text analysis...")
            return _parse_fallback_response(file_content)
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"ERROR in _analyze_with_ai: {e}")
        return None


def _generate_json_schema() -> str:
    """
    Generuje JSON Schema dla odpowiedzi AI na podstawie modeli Pydantic.
    
    Returns:
        str: JSON Schema jako string
    """
    
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string", "description": "Nazwa strategii komunikacji"},
            "description": {"type": "string", "description": "Opis strategii"},
            "communication_goals": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista celów komunikacyjnych"
            },
            "target_audiences": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"}
                    },
                    "required": ["name", "description"]
                },
                "description": "Lista person docelowych"
            },
            "general_style": {
                "type": "object",
                "properties": {
                    "language": {"type": "string"},
                    "tone": {"type": "string"},
                    "technical_content": {"type": "string"},
                    "employer_branding_content": {"type": "string"}
                },
                "description": "Ogólny styl komunikacji"
            },
            "platform_styles": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "platform_name": {"type": "string"},
                        "length_description": {"type": "string"},
                        "style_description": {"type": "string"},
                        "notes": {"type": "string"}
                    },
                    "required": ["platform_name", "length_description", "style_description"]
                },
                "description": "Style dla konkretnych platform"
            },
            "forbidden_phrases": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista zakazanych zwrotów"
            },
            "preferred_phrases": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista preferowanych zwrotów"
            },
            "cta_rules": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "content_type": {"type": "string"},
                        "cta_text": {"type": "string"}
                    },
                    "required": ["content_type", "cta_text"]
                },
                "description": "Reguły Call-to-Action"
            },
            "sample_content_types": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Lista przykładowych typów treści"
            }
        },
        "required": ["name"]
    }
    
    return json.dumps(schema, indent=2)


def _call_gemini_api(prompt: str, model_name: str, max_retries: int = 3) -> Optional[str]:
    """
    Wywołuje Google Gemini API do analizy strategii komunikacji z retry logic.
    
    Args:
        prompt: Sformatowany prompt do analizy
        model_name: Nazwa modelu Gemini
        max_retries: Maximum number of retries for rate limiting
        
    Returns:
        str: Odpowiedź AI w formacie JSON lub None w przypadku błędu
    """
    
    if not GEMINI_API_AVAILABLE:
        print("WARNING: Google AI SDK not available, using fallback")
        return None
    
    # Konfiguracja API key z zmiennej środowiskowej
    api_key = os.getenv('GOOGLE_AI_API_KEY')
    if not api_key:
        print("ERROR: GOOGLE_AI_API_KEY environment variable not set")
        return None
        
    # Konfiguracja Gemini API
    genai.configure(api_key=api_key)
    
    import time
    
    for attempt in range(max_retries):
        try:
            # Tworzenie modelu
            model = genai.GenerativeModel(model_name)
            
            # Generowanie odpowiedzi
            try:
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,  # Niska temperatura dla precyzyjnych wyników
                        max_output_tokens=8192,  # Zwiększony limit dla dłuższych blogów
                        response_mime_type="application/json"  # Wymuszenie JSON
                    )
                )
            except Exception as e:
                # Fallback without response_mime_type if not supported
                if attempt == 0:  # Only log on first attempt
                    print(f"Trying without response_mime_type due to error: {e}")
                response = model.generate_content(
                    prompt,
                    generation_config=genai.types.GenerationConfig(
                        temperature=0.1,
                        max_output_tokens=8192  # Zwiększony limit dla dłuższych blogów
                    )
                )
            
            if response and response.text:
                return response.text.strip()
            else:
                print("ERROR: Empty response from Gemini API")
                return None
                
        except Exception as e:
            error_str = str(e).lower()
            
            # Check for rate limiting error
            if any(keyword in error_str for keyword in ["quota", "429", "resource_exhausted", "rate_limit", "too many requests"]):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) * 10  # Exponential backoff: 10s, 20s, 40s
                    print(f"Rate limit hit, waiting {wait_time} seconds before retry {attempt + 1}/{max_retries}")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"Rate limit exceeded after {max_retries} attempts")
                    return None
            else:
                print(f"ERROR calling Gemini API: {str(e)}")
                return None
    
    return None


def _parse_fallback_response(file_content: str) -> Optional[Dict[str, Any]]:
    """
    Fallback parsing w przypadku błędu Gemini API.
    Próbuje wyodrębnić podstawowe informacje z tekstu.
    
    Args:
        file_content: Zawartość pliku do analizy
        
    Returns:
        dict: Podstawowe dane strategii lub None
    """
    
    try:
        # Analiza tekstu w poszukiwaniu nazwy strategii
        lines = file_content.split('\n')
        strategy_name = "Strategia komunikacji z analizy tekstu"
        
        # Próba znalezienia tytułu w pierwszych liniach
        for line in lines[:5]:
            if line.strip() and len(line.strip()) > 10:
                strategy_name = line.strip()[:100]  # Ograniczenie długości
                break
        
        # Podstawowa odpowiedź
        fallback_response = {
            "name": strategy_name,
            "description": f"Strategia komunikacji wyodrębniona z dokumentu o długości {len(file_content)} znaków",
            "communication_goals": ["Cel wymagający dalszej analizy"],
            "target_audiences": [{
                "name": "Grupa docelowa wymagająca analizy",
                "description": "Wymaga dalszej analizy dokumentu"
            }],
            "general_style": {
                "language": "polski",
                "tone": "do ustalenia",
                "technical_content": "wymaga analizy",
                "employer_branding_content": "wymaga analizy"
            },
            "platform_styles": [],
            "forbidden_phrases": [],
            "preferred_phrases": [],
            "cta_rules": [],
            "sample_content_types": []
        }
        
        return fallback_response
        
    except Exception as e:
        print(f"ERROR in fallback parsing: {e}")
        return None


def _simulate_ai_response(file_content: str) -> str:
    """
    Symuluje odpowiedź AI - do zastąpienia rzeczywistym wywołaniem API.
    
    Args:
        file_content: Zawartość pliku do analizy
        
    Returns:
        str: Przykładowa odpowiedź AI w formacie JSON
    """
    
    # Przykładowa odpowiedź AI
    sample_response = {
        "name": "Strategia komunikacji testowa",
        "description": "Strategia komunikacji oparta na analizie dostarczonych danych",
        "communication_goals": [
            "Zwiększenie świadomości marki",
            "Pozyskanie nowych klientów",
            "Budowanie zaufania"
        ],
        "target_audiences": [
            {
                "name": "Młodzi profesjonaliści",
                "description": "Osoby w wieku 25-35 lat z wykształceniem wyższym"
            },
            {
                "name": "Przedsiębiorcy",
                "description": "Właściciele małych i średnich firm"
            }
        ],
        "general_style": {
            "language": "polski",
            "tone": "profesjonalny i przyjazny",
            "technical_content": "Upraszczanie terminów technicznych dla szerszej publiczności",
            "employer_branding_content": "Eksponowanie wartości firmy i kultury organizacyjnej"
        },
        "platform_styles": [
            {
                "platform_name": "LinkedIn",
                "length_description": "Posty 100-200 słów",
                "style_description": "Profesjonalny, ekspertowy, networking",
                "notes": "Używanie hashtagów branżowych"
            },
            {
                "platform_name": "Facebook",
                "length_description": "Posty 50-150 słów",
                "style_description": "Więcej emocji, storytelling",
                "notes": "Dodawanie zdjęć i grafik"
            }
        ],
        "forbidden_phrases": [
            "sprzedaż agresywna",
            "błyskawiczny zysk",
            "najlepszy na rynku"
        ],
        "preferred_phrases": [
            "wartość dodana",
            "rozwiązanie biznesowe",
            "partnerstwo strategiczne"
        ],
        "cta_rules": [
            {
                "content_type": "post LinkedIn",
                "cta_text": "Skontaktuj się z nami"
            },
            {
                "content_type": "post Facebook",
                "cta_text": "Dowiedz się więcej"
            }
        ],
        "sample_content_types": [
            "post LinkedIn",
            "post Facebook",
            "artykuł blogowy",
            "newsletter",
            "case study"
        ]
    }
    
    return json.dumps(sample_response, ensure_ascii=False, indent=2)


def _save_to_database(strategy_data: CommunicationStrategyCreate, created_by_id: int) -> Optional[int]:
    """
    Zapisuje strategię komunikacji do znormalizowanej bazy danych.
    
    Args:
        strategy_data: Dane strategii do zapisu
        created_by_id: ID użytkownika tworzącego strategię
        
    Returns:
        int: ID utworzonej strategii lub None w przypadku błędu
    """
    
    print(f"DEBUG: Saving strategy to database...")
    print(f"DEBUG: Strategy name: {strategy_data.name}")
    print(f"DEBUG: Communication goals: {len(strategy_data.communication_goals)} goals")
    print(f"DEBUG: Target audiences: {len(strategy_data.target_audiences)} audiences")
    
    try:
        # Tworzenie sesji bazy danych
        db = SessionLocal()
        
        try:
            # Rozpoczęcie transakcji
            db.begin()
            
            # Tworzenie głównej strategii
            main_strategy = CommunicationStrategy(
                name=strategy_data.name,
                description=strategy_data.description,
                organization_id=strategy_data.organization_id,
                created_by_id=created_by_id,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(main_strategy)
            db.flush()  # Pobieramy ID bez commitowania
            
            strategy_id = main_strategy.id
            
            # Zapisywanie celów komunikacyjnych
            for goal in strategy_data.communication_goals:
                goal_obj = CommunicationGoal(
                    communication_strategy_id=strategy_id,
                    goal_text=goal
                )
                db.add(goal_obj)
            
            # Zapisywanie person docelowych
            for persona_data in strategy_data.target_audiences:
                persona_obj = Persona(
                    communication_strategy_id=strategy_id,
                    name=persona_data.name,
                    description=persona_data.description,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(persona_obj)
            
            # Zapisywanie ogólnego stylu
            if strategy_data.general_style:
                general_style_obj = GeneralStyle(
                    communication_strategy_id=strategy_id,
                    language=strategy_data.general_style.language,
                    tone=strategy_data.general_style.tone,
                    technical_content=strategy_data.general_style.technical_content,
                    employer_branding_content=strategy_data.general_style.employer_branding_content,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(general_style_obj)
            
            # Zapisywanie stylów platformowych
            for platform_style_data in strategy_data.platform_styles:
                platform_style_obj = PlatformStyle(
                    communication_strategy_id=strategy_id,
                    platform_name=platform_style_data.platform_name,
                    length_description=platform_style_data.length_description,
                    style_description=platform_style_data.style_description,
                    notes=platform_style_data.notes,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(platform_style_obj)
            
            # Zapisywanie zakazanych zwrotów
            for phrase in strategy_data.forbidden_phrases:
                forbidden_phrase_obj = ForbiddenPhrase(
                    communication_strategy_id=strategy_id,
                    phrase=phrase
                )
                db.add(forbidden_phrase_obj)
            
            # Zapisywanie preferowanych zwrotów
            for phrase in strategy_data.preferred_phrases:
                preferred_phrase_obj = PreferredPhrase(
                    communication_strategy_id=strategy_id,
                    phrase=phrase
                )
                db.add(preferred_phrase_obj)
            
            # Zapisywanie reguł CTA
            for cta_rule_data in strategy_data.cta_rules:
                cta_rule_obj = CTARule(
                    communication_strategy_id=strategy_id,
                    content_type=cta_rule_data.content_type,
                    cta_text=cta_rule_data.cta_text,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                db.add(cta_rule_obj)
            
            # Zapisywanie przykładowych typów treści
            for content_type in strategy_data.sample_content_types:
                sample_content_obj = SampleContentType(
                    communication_strategy_id=strategy_id,
                    content_type=content_type
                )
                db.add(sample_content_obj)
            
            # Commitowanie transakcji
            db.commit()
            
            return strategy_id
            
        except Exception as e:
            db.rollback()
            print(f"ERROR saving to database: {e}")
            return None
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"ERROR in _save_to_database: {e}")
        return None 