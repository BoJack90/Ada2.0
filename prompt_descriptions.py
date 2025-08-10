"""
Opisy dla promptów AI używanych w systemie Ada 2.0
"""

PROMPT_DESCRIPTIONS = {
    # Generowanie treści
    "generate_single_variant": "Generuje pojedynczy wariant treści dla określonej platformy społecznościowej na podstawie tematu",
    "generate_blog_content": "Tworzy pełną treść artykułu blogowego wraz ze strukturą, nagłówkami i formatowaniem",
    "generate_blog_topics_for_selection": "Generuje listę propozycji tematów blogowych do wyboru na podstawie strategii komunikacji",
    
    # Social Media
    "generate_sm_variants_from_blog_context": "Tworzy posty na social media powiązane z konkretnym artykułem blogowym",
    "generate_standalone_sm_posts": "Generuje samodzielne posty na social media niezwiązane z blogami",
    "generate_sm_from_brief": "Tworzy posty SM na podstawie informacji z briefu komunikacyjnego",
    
    # Planowanie i harmonogram
    "schedule_topics": "Generuje optymalny harmonogram publikacji treści z uwzględnieniem dat i platform",
    
    # Analiza dokumentów
    "strategy_parser": "Analizuje i ekstraktuje kluczowe informacje ze strategii komunikacji w formacie PDF/DOC",
    "analyze_brief": "Wyodrębnia istotne informacje z briefów komunikacyjnych (tematy, instrukcje, aktualności)",
    
    # Deep Reasoning
    "analyze_task_requirements": "Pierwszy krok Deep Reasoning - analizuje wymagania zadania",
    "generate_initial_solution": "Drugi krok Deep Reasoning - generuje wstępne rozwiązanie",
    "identify_gaps_and_improvements": "Trzeci krok Deep Reasoning - identyfikuje luki i możliwości poprawy",
    "refine_solution": "Czwarty krok Deep Reasoning - udoskonala rozwiązanie",
    "final_review_and_polish": "Piąty krok Deep Reasoning - finalna weryfikacja i dopracowanie",
    
    # Inne
    "review_content": "Recenzuje i ocenia wygenerowaną treść pod kątem jakości i zgodności ze strategią",
    "improve_content": "Poprawia treść na podstawie uwag recenzenta",
    "extract_key_messages": "Wyodrębnia kluczowe komunikaty z dokumentów strategicznych",
}

# Kategorie promptów dla lepszej organizacji
PROMPT_CATEGORIES = {
    "content_generation": {
        "name": "Generowanie treści",
        "description": "Prompty do tworzenia artykułów i postów",
        "prompts": ["generate_single_variant", "generate_blog_content", "generate_blog_topics_for_selection"]
    },
    "social_media": {
        "name": "Social Media",
        "description": "Prompty specyficzne dla platform społecznościowych",
        "prompts": ["generate_sm_variants_from_blog_context", "generate_standalone_sm_posts", "generate_sm_from_brief"]
    },
    "planning": {
        "name": "Planowanie",
        "description": "Harmonogramowanie i organizacja publikacji",
        "prompts": ["schedule_topics"]
    },
    "analysis": {
        "name": "Analiza dokumentów",
        "description": "Przetwarzanie i analiza briefów oraz strategii",
        "prompts": ["strategy_parser", "analyze_brief", "extract_key_messages"]
    },
    "deep_reasoning": {
        "name": "Deep Reasoning",
        "description": "Zaawansowany proces generowania z wieloma krokami",
        "prompts": ["analyze_task_requirements", "generate_initial_solution", "identify_gaps_and_improvements", "refine_solution", "final_review_and_polish"]
    },
    "review": {
        "name": "Recenzja i poprawa",
        "description": "Ocena i ulepszanie wygenerowanych treści",
        "prompts": ["review_content", "improve_content"]
    }
}