from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.crud import AIPromptCRUD, AIModelAssignmentCRUD
from app.db.schemas import AIPromptCreate, AIPromptUpdate, AIPrompt, AIModelAssignmentCreate, AIModelAssignmentUpdate, AIModelAssignment
from app.db.database import get_db
from app.core.dependencies import get_current_active_user
from app.db.models import User, OrganizationAIPrompt, OrganizationAIModelAssignment, Organization
from app.core.prompt_manager import PromptManager
from app.core.ai_config_service import AIConfigService

router = APIRouter()

# Dostępne modele Gemini
AVAILABLE_MODELS = [
    "gemini-2.5-pro",
    "gemini-2.5-flash",
    "gemini-2.5-pro-latest",
    "gemini-2.5-flash-latest",
    "gemini-2.0-flash",
    "gemini-2.0-flash-exp",
    "gemini-1.5-pro-latest",
    "gemini-1.5-flash-latest",
    "gemini-1.5-flash-8b-latest",
    "gemini-1.0-pro-latest",
    "gemini-1.0-pro-vision-latest",
    "gemini-pro",
    "gemini-pro-vision",
    "gemini-flash",
    "gemini-flash-8b"
]

@router.get("/ai-models", response_model=List[str])
async def get_available_models(current_user: User = Depends(get_current_active_user)):
    """Pobiera listę dostępnych modeli Gemini"""
    return AVAILABLE_MODELS

@router.get("/ai-prompts", response_model=List[AIPrompt])
async def get_ai_prompts(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera wszystkie prompty AI"""
    crud = AIPromptCRUD()
    return crud.get_all(db)

@router.post("/ai-prompts", response_model=AIPrompt)
async def create_ai_prompt(
    prompt_data: AIPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tworzy nowy prompt AI"""
    crud = AIPromptCRUD()
    return crud.create(db, prompt_data)

@router.get("/ai-prompts/{prompt_id}", response_model=AIPrompt)
async def get_ai_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera pojedynczy prompt AI"""
    crud = AIPromptCRUD()
    prompt = crud.get_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt nie został znaleziony"
        )
    return prompt

@router.put("/ai-prompts/{prompt_id}", response_model=AIPrompt)
async def update_ai_prompt(
    prompt_id: int,
    prompt_data: AIPromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aktualizuje prompt AI"""
    crud = AIPromptCRUD()
    prompt = crud.get_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt nie został znaleziony"
        )
    return crud.update(db, prompt_id, prompt_data)

@router.delete("/ai-prompts/{prompt_id}")
async def delete_ai_prompt(
    prompt_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Usuwa prompt AI"""
    crud = AIPromptCRUD()
    prompt = crud.get_by_id(db, prompt_id)
    if not prompt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Prompt nie został znaleziony"
        )
    crud.delete(db, prompt_id)
    return {"message": "Prompt został usunięty"}

@router.get("/ai-model-assignments", response_model=List[AIModelAssignment])
async def get_ai_model_assignments(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera wszystkie przypisania modeli AI"""
    crud = AIModelAssignmentCRUD()
    return crud.get_all(db)

@router.post("/ai-model-assignments", response_model=AIModelAssignment)
async def create_ai_model_assignment(
    assignment_data: AIModelAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tworzy nowe przypisanie modelu AI"""
    # Sprawdź czy model jest dostępny
    if assignment_data.model_name not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {assignment_data.model_name} nie jest dostępny"
        )
    
    crud = AIModelAssignmentCRUD()
    return crud.create(db, assignment_data)

@router.get("/ai-model-assignments/{assignment_id}", response_model=AIModelAssignment)
async def get_ai_model_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera pojedyncze przypisanie modelu AI"""
    crud = AIModelAssignmentCRUD()
    assignment = crud.get_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Przypisanie modelu nie zostało znalezione"
        )
    return assignment

@router.put("/ai-model-assignments/{assignment_id}", response_model=AIModelAssignment)
async def update_ai_model_assignment(
    assignment_id: int,
    assignment_data: AIModelAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aktualizuje przypisanie modelu AI"""
    # Sprawdź czy model jest dostępny (jeśli został podany)
    if assignment_data.model_name and assignment_data.model_name not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {assignment_data.model_name} nie jest dostępny"
        )
    
    crud = AIModelAssignmentCRUD()
    assignment = crud.get_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Przypisanie modelu nie zostało znalezione"
        )
    return crud.update(db, assignment_id, assignment_data)

@router.delete("/ai-model-assignments/{assignment_id}")
async def delete_ai_model_assignment(
    assignment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Usuwa przypisanie modelu AI"""
    crud = AIModelAssignmentCRUD()
    assignment = crud.get_by_id(db, assignment_id)
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Przypisanie modelu nie zostało znalezione"
        )
    crud.delete(db, assignment_id)
    return {"message": "Przypisanie modelu zostało usunięte"}

@router.get("/ai-functions")
async def get_ai_functions_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera przegląd wszystkich funkcji AI z ich promptami i modelami"""
    prompt_crud = AIPromptCRUD()
    model_crud = AIModelAssignmentCRUD()
    
    # Pobierz wszystkie prompty i modele
    prompts = prompt_crud.get_all(db)
    models = model_crud.get_all(db)
    
    # Grupuj prompty według nazw (prompt_name odpowiada task_name)
    functions = {}
    for prompt in prompts:
        if prompt.prompt_name not in functions:
            functions[prompt.prompt_name] = {
                "function_name": prompt.prompt_name,
                "prompts": [],
                "model_assignment": None
            }
        functions[prompt.prompt_name]["prompts"].append(prompt)
    
    # Dodaj przypisania modeli (łącząc task_name z prompt_name)
    for model in models:
        if model.task_name in functions:
            functions[model.task_name]["model_assignment"] = model
    
    return {
        "functions": list(functions.values()),
        "total_functions": len(functions),
        "total_prompts": len(prompts),
        "total_model_assignments": len(models),
        "available_models": AVAILABLE_MODELS
    }

@router.get("/ai-functions/grouped")
async def get_ai_functions_grouped(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera funkcje AI pogrupowane według kategorii dla lepszej organizacji"""
    prompt_crud = AIPromptCRUD()
    model_crud = AIModelAssignmentCRUD()
    
    prompts = prompt_crud.get_all(db)
    models = model_crud.get_all(db)
    
    # Definiuj kategorie funkcji AI
    categories = {
        "content_generation": {
            "name": "Generowanie Treści",
            "description": "Funkcje odpowiedzialne za tworzenie różnych typów treści",
            "icon": "edit",
            "functions": []
        },
        "analysis": {
            "name": "Analiza i Przetwarzanie",
            "description": "Funkcje analizy strategii i danych",
            "icon": "analytics",
            "functions": []
        },
        "management": {
            "name": "Zarządzanie",
            "description": "Funkcje zarządzania i organizacji treści",
            "icon": "settings",
            "functions": []
        },
        "other": {
            "name": "Inne",
            "description": "Pozostałe funkcje AI",
            "icon": "more",
            "functions": []
        }
    }
    
    # Mapowanie nazw funkcji do kategorii
    function_categories = {
        "blog_topics_generation": "content_generation",
        "content_draft_generation": "content_generation", 
        "variant_generation": "content_generation",
        "variant_revision": "content_generation",
        "sm_correlation": "content_generation",
        "scheduling": "management",
        "strategy_parser": "analysis",
        "single_variant_generation": "content_generation"
    }
    
    # Grupuj prompty według funkcji
    functions = {}
    for prompt in prompts:
        if prompt.prompt_name not in functions:
            functions[prompt.prompt_name] = {
                "function_name": prompt.prompt_name,
                "display_name": prompt.prompt_name.replace("_", " ").title(),
                "prompts": [],
                "model_assignment": None,
                "category": function_categories.get(prompt.prompt_name, "other")
            }
        functions[prompt.prompt_name]["prompts"].append(prompt)
    
    # Dodaj przypisania modeli
    for model in models:
        if model.task_name in functions:
            functions[model.task_name]["model_assignment"] = model
    
    # Organizuj funkcje według kategorii
    for function_name, function_data in functions.items():
        category = function_data["category"]
        if category in categories:
            categories[category]["functions"].append(function_data)
    
    return {
        "categories": categories,
        "total_functions": len(functions),
        "total_prompts": len(prompts),
        "total_model_assignments": len(models),
        "available_models": AVAILABLE_MODELS
    }

@router.get("/ai-functions/health")
async def get_ai_functions_health(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Sprawdza stan konfiguracji AI - czy wszystkie funkcje mają przypisane modele"""
    prompt_crud = AIPromptCRUD()
    model_crud = AIModelAssignmentCRUD()
    
    prompts = prompt_crud.get_all(db)
    models = model_crud.get_all(db)
    
    # Pobierz unikalne nazwy funkcji
    function_names = list(set(prompt.prompt_name for prompt in prompts))
    model_task_names = list(set(model.task_name for model in models))
    
    # Sprawdź stan konfiguracji
    configured_functions = []
    missing_model_assignments = []
    orphaned_models = []
    
    for function_name in function_names:
        if function_name in model_task_names:
            configured_functions.append(function_name)
        else:
            missing_model_assignments.append(function_name)
    
    for model_name in model_task_names:
        if model_name not in function_names:
            orphaned_models.append(model_name)
    
    health_score = len(configured_functions) / len(function_names) if function_names else 0
    
    return {
        "health_score": health_score,
        "status": "healthy" if health_score >= 0.9 else "warning" if health_score >= 0.7 else "critical",
        "total_functions": len(function_names),
        "configured_functions": len(configured_functions),
        "missing_model_assignments": missing_model_assignments,
        "orphaned_models": orphaned_models,
        "recommendations": [
            f"Przypisz model do funkcji: {', '.join(missing_model_assignments)}" if missing_model_assignments else None,
            f"Usuń niepotrzebne przypisania: {', '.join(orphaned_models)}" if orphaned_models else None
        ]
    } 


# Organization-specific AI endpoints
@router.get("/organizations/{organization_id}/ai-prompts", response_model=List[AIPrompt])
async def get_organization_ai_prompts(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera prompty AI dla organizacji (łącznie z globalnymi)"""
    # Check if user has access to organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get organization-specific prompts
    org_prompts = db.query(OrganizationAIPrompt)\
        .filter(OrganizationAIPrompt.organization_id == organization_id)\
        .filter(OrganizationAIPrompt.is_active == True)\
        .all()
    
    # Get global prompts
    global_prompts = AIPromptCRUD().get_all(db)
    
    # Merge prompts (org prompts override global)
    prompt_dict = {p.prompt_name: p for p in global_prompts}
    for org_prompt in org_prompts:
        prompt_dict[org_prompt.prompt_name] = org_prompt
    
    return list(prompt_dict.values())


@router.post("/organizations/{organization_id}/ai-prompts", response_model=AIPrompt)
async def create_organization_ai_prompt(
    organization_id: int,
    prompt_data: AIPromptCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tworzy nowy prompt AI dla organizacji"""
    # Check if user has access to organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if prompt already exists for this org
    existing = db.query(OrganizationAIPrompt)\
        .filter(OrganizationAIPrompt.organization_id == organization_id)\
        .filter(OrganizationAIPrompt.prompt_name == prompt_data.prompt_name)\
        .first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Prompt already exists for this organization")
    
    # Create new org prompt
    new_prompt = OrganizationAIPrompt(
        organization_id=organization_id,
        prompt_name=prompt_data.prompt_name,
        prompt_template=prompt_data.prompt_template,
        created_by_id=current_user.id,
        is_active=True,
        version=1
    )
    
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    return new_prompt


@router.put("/organizations/{organization_id}/ai-prompts/{prompt_id}", response_model=AIPrompt)
async def update_organization_ai_prompt(
    organization_id: int,
    prompt_id: int,
    prompt_data: AIPromptUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aktualizuje prompt AI dla organizacji"""
    # Try to find organization-specific prompt first
    org_prompt = db.query(OrganizationAIPrompt)\
        .filter(OrganizationAIPrompt.organization_id == organization_id)\
        .filter(OrganizationAIPrompt.id == prompt_id)\
        .first()
    
    if org_prompt:
        # Update org prompt
        if prompt_data.prompt_template:
            org_prompt.prompt_template = prompt_data.prompt_template
            org_prompt.version += 1
        db.commit()
        db.refresh(org_prompt)
        return org_prompt
    
    # If not found, check if it's a global prompt
    global_prompt = db.query(AIPrompt).filter(AIPrompt.id == prompt_id).first()
    if not global_prompt:
        raise HTTPException(status_code=404, detail="Prompt not found")
    
    # Create organization-specific override
    new_prompt = OrganizationAIPrompt(
        organization_id=organization_id,
        prompt_name=global_prompt.prompt_name,
        prompt_template=prompt_data.prompt_template or global_prompt.prompt_template,
        base_prompt_id=global_prompt.id,
        created_by_id=current_user.id,
        is_active=True,
        version=1
    )
    
    db.add(new_prompt)
    db.commit()
    db.refresh(new_prompt)
    
    return new_prompt


@router.get("/organizations/{organization_id}/ai-model-assignments", response_model=List[AIModelAssignment])
async def get_organization_ai_model_assignments(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera przypisania modeli AI dla organizacji"""
    # Check if user has access to organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Get organization-specific assignments
    org_assignments = db.query(OrganizationAIModelAssignment)\
        .filter(OrganizationAIModelAssignment.organization_id == organization_id)\
        .filter(OrganizationAIModelAssignment.is_active == True)\
        .all()
    
    # Get global assignments
    global_assignments = AIModelAssignmentCRUD().get_all(db)
    
    # Merge assignments (org assignments override global)
    assignment_dict = {a.task_name: a for a in global_assignments}
    for org_assignment in org_assignments:
        assignment_dict[org_assignment.task_name] = org_assignment
    
    return list(assignment_dict.values())


@router.post("/organizations/{organization_id}/ai-model-assignments", response_model=AIModelAssignment)
async def create_organization_ai_model_assignment(
    organization_id: int,
    assignment_data: AIModelAssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Tworzy nowe przypisanie modelu AI dla organizacji"""
    # Check if user has access to organization
    org = db.query(Organization).filter(Organization.id == organization_id).first()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")
    
    # Check if model is available
    if assignment_data.model_name not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {assignment_data.model_name} nie jest dostępny"
        )
    
    # Check if assignment already exists for this org
    existing = db.query(OrganizationAIModelAssignment)\
        .filter(OrganizationAIModelAssignment.organization_id == organization_id)\
        .filter(OrganizationAIModelAssignment.task_name == assignment_data.task_name)\
        .first()
    
    if existing:
        # Update existing
        existing.model_name = assignment_data.model_name
        existing.is_active = True
        db.commit()
        db.refresh(existing)
        return existing
    
    # Create new org assignment
    new_assignment = OrganizationAIModelAssignment(
        organization_id=organization_id,
        task_name=assignment_data.task_name,
        model_name=assignment_data.model_name,
        created_by_id=current_user.id,
        is_active=True
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return new_assignment


@router.put("/organizations/{organization_id}/ai-model-assignments/{assignment_id}", response_model=AIModelAssignment)
async def update_organization_ai_model_assignment(
    organization_id: int,
    assignment_id: int,
    assignment_data: AIModelAssignmentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Aktualizuje przypisanie modelu AI dla organizacji"""
    # Check if model is available (if provided)
    if assignment_data.model_name and assignment_data.model_name not in AVAILABLE_MODELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Model {assignment_data.model_name} nie jest dostępny"
        )
    
    # Try to find organization-specific assignment first
    org_assignment = db.query(OrganizationAIModelAssignment)\
        .filter(OrganizationAIModelAssignment.organization_id == organization_id)\
        .filter(OrganizationAIModelAssignment.id == assignment_id)\
        .first()
    
    if org_assignment:
        # Update org assignment
        if assignment_data.model_name:
            org_assignment.model_name = assignment_data.model_name
        db.commit()
        db.refresh(org_assignment)
        return org_assignment
    
    # If not found, check if it's a global assignment
    global_assignment = db.query(AIModelAssignment).filter(AIModelAssignment.id == assignment_id).first()
    if not global_assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Create organization-specific override
    new_assignment = OrganizationAIModelAssignment(
        organization_id=organization_id,
        task_name=global_assignment.task_name,
        model_name=assignment_data.model_name or global_assignment.model_name,
        base_assignment_id=global_assignment.id,
        created_by_id=current_user.id,
        is_active=True
    )
    
    db.add(new_assignment)
    db.commit()
    db.refresh(new_assignment)
    
    return new_assignment


@router.get("/organizations/{organization_id}/ai-functions/grouped")
async def get_organization_ai_functions_grouped(
    organization_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Pobiera funkcje AI pogrupowane według kategorii dla organizacji"""
    # Get prompt manager and AI config for organization
    prompt_manager = PromptManager(db, organization_id)
    ai_config = AIConfigService(db, organization_id)
    
    # Use the same logic as global endpoint but with org context
    prompt_crud = AIPromptCRUD()
    model_crud = AIModelAssignmentCRUD()
    
    # Get all prompts (global + org specific)
    global_prompts = prompt_crud.get_all(db)
    org_prompts = db.query(OrganizationAIPrompt)\
        .filter(OrganizationAIPrompt.organization_id == organization_id)\
        .filter(OrganizationAIPrompt.is_active == True)\
        .all()
    
    # Get all model assignments (global + org specific)
    global_models = model_crud.get_all(db)
    org_models = db.query(OrganizationAIModelAssignment)\
        .filter(OrganizationAIModelAssignment.organization_id == organization_id)\
        .filter(OrganizationAIModelAssignment.is_active == True)\
        .all()
    
    # Merge prompts and models
    prompt_dict = {p.prompt_name: p for p in global_prompts}
    for org_prompt in org_prompts:
        prompt_dict[org_prompt.prompt_name] = org_prompt
    
    model_dict = {m.task_name: m for m in global_models}
    for org_model in org_models:
        model_dict[org_model.task_name] = org_model
    
    # Rest of the logic same as global endpoint
    categories = {
        "content_generation": {
            "name": "Generowanie Treści",
            "description": "Funkcje odpowiedzialne za tworzenie różnych typów treści",
            "icon": "edit",
            "functions": []
        },
        "analysis": {
            "name": "Analiza i Przetwarzanie",
            "description": "Funkcje analizy strategii i danych",
            "icon": "analytics",
            "functions": []
        },
        "management": {
            "name": "Zarządzanie",
            "description": "Funkcje zarządzania i organizacji treści",
            "icon": "settings",
            "functions": []
        },
        "other": {
            "name": "Inne",
            "description": "Pozostałe funkcje AI",
            "icon": "more",
            "functions": []
        }
    }
    
    # Function category mapping
    function_categories = {
        "blog_topics_generation": "content_generation",
        "content_draft_generation": "content_generation", 
        "variant_generation": "content_generation",
        "variant_revision": "content_generation",
        "sm_correlation": "content_generation",
        "scheduling": "management",
        "strategy_parser": "analysis",
        "single_variant_generation": "content_generation"
    }
    
    # Build functions list
    functions = {}
    for prompt_name, prompt in prompt_dict.items():
        if prompt_name not in functions:
            functions[prompt_name] = {
                "function_name": prompt_name,
                "display_name": prompt_name.replace("_", " ").title(),
                "prompts": [],
                "model_assignment": None,
                "category": function_categories.get(prompt_name, "other")
            }
        functions[prompt_name]["prompts"].append(prompt)
    
    # Add model assignments
    for task_name, model in model_dict.items():
        if task_name in functions:
            functions[task_name]["model_assignment"] = model
    
    # Organize by category
    for function_name, function_data in functions.items():
        category = function_data["category"]
        if category in categories:
            categories[category]["functions"].append(function_data)
    
    return {
        "categories": categories,
        "total_functions": len(functions),
        "total_prompts": len(prompt_dict),
        "total_model_assignments": len(model_dict),
        "available_models": AVAILABLE_MODELS
    }
