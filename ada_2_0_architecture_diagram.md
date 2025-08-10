# Ada 2.0 - Graf Logiki Działania Aplikacji

## Architektura Systemu

```mermaid
graph TB
    %% Frontend Layer
    subgraph "Frontend (Next.js)"
        UI[Interfejs Użytkownika]
        AUTH[Strona Logowania]
        DASH[Dashboard]
        ORG[Zarządzanie Organizacjami]
        CONTENT[Plany Treści]
        DRAFTS[Szkice Treści]
        SETTINGS[Ustawienia]
    end

    %% API Layer
    subgraph "Backend API (FastAPI)"
        API[FastAPI Router]
        AUTH_API[Auth API]
        ORG_API[Organizations API]
        CONTENT_API[Content Plans API]
        DRAFTS_API[Content Drafts API]
        TASKS_API[Tasks API]
        AI_API[AI Management API]
    end

    %% Business Logic Layer
    subgraph "Logika Biznesowa"
        AUTH_SERVICE[Uwierzytelnianie]
        ORG_SERVICE[Zarządzanie Organizacjami]
        CONTENT_SERVICE[Generowanie Treści]
        STRATEGY_SERVICE[Strategie Komunikacji]
        SCHEDULING_SERVICE[Harmonogramowanie]
    end

    %% Background Processing
    subgraph "Przetwarzanie w Tle (Celery)"
        CELERY[Celery Worker]
        CONTEXTUALIZE[Kontekstualizacja]
        GENERATE_BLOG[Generowanie Tematów Blog]
        GENERATE_SM[Generowanie SM]
        SCHEDULE[Harmonogramowanie]
    end

    %% AI Integration
    subgraph "Integracja AI"
        GEMINI[Google Gemini API]
        PROMPTS[Zarządzanie Promptami]
        AI_CONFIG[Konfiguracja AI]
        TAVILY[Tavily Research API]
    end

    %% Database Layer
    subgraph "Baza Danych (PostgreSQL)"
        USERS[Użytkownicy]
        ORGANIZATIONS[Organizacje]
        CONTENT_PLANS[Plany Treści]
        SUGGESTED_TOPICS[Sugerowane Tematy]
        CONTENT_DRAFTS[Szkice Treści]
        CONTENT_VARIANTS[Warianty Treści]
        COMMUNICATION_STRATEGIES[Strategie Komunikacji]
        TASKS[Zadania]
        AI_PROMPTS[Prompty AI]
    end

    %% Cache & Queue
    subgraph "Cache i Kolejki (Redis)"
        REDIS[Redis]
        CACHE[Cache]
        QUEUE[Kolejka Zadań]
    end

    %% Connections
    UI --> API
    AUTH --> AUTH_API
    DASH --> ORG_API
    DASH --> CONTENT_API
    ORG --> ORG_API
    CONTENT --> CONTENT_API
    DRAFTS --> DRAFTS_API
    SETTINGS --> AI_API

    API --> AUTH_SERVICE
    API --> ORG_SERVICE
    API --> CONTENT_SERVICE
    API --> STRATEGY_SERVICE

    AUTH_SERVICE --> USERS
    ORG_SERVICE --> ORGANIZATIONS
    CONTENT_SERVICE --> CONTENT_PLANS
    CONTENT_SERVICE --> CELERY
    STRATEGY_SERVICE --> COMMUNICATION_STRATEGIES

    CELERY --> CONTEXTUALIZE
    CONTEXTUALIZE --> GENERATE_BLOG
    GENERATE_BLOG --> GENERATE_SM
    GENERATE_SM --> SCHEDULE

    CONTEXTUALIZE --> COMMUNICATION_STRATEGIES
    GENERATE_BLOG --> GEMINI
    GENERATE_BLOG --> PROMPTS
    GENERATE_SM --> GEMINI
    GENERATE_SM --> TAVILY

    PROMPTS --> AI_PROMPTS
    AI_CONFIG --> AI_PROMPTS

    CELERY --> REDIS
    CACHE --> REDIS
    QUEUE --> REDIS

    GENERATE_BLOG --> SUGGESTED_TOPICS
    GENERATE_SM --> CONTENT_DRAFTS
    GENERATE_SM --> CONTENT_VARIANTS
    SCHEDULE --> TASKS
```

## Przepływ Głównych Procesów

### 1. Proces Uwierzytelniania
```mermaid
sequenceDiagram
    participant U as Użytkownik
    participant F as Frontend
    participant A as Auth API
    participant DB as Database

    U->>F: Logowanie (email/hasło)
    F->>A: POST /auth/login
    A->>DB: Weryfikacja użytkownika
    DB-->>A: Dane użytkownika
    A-->>F: JWT Token
    F-->>U: Przekierowanie do Dashboard
```

### 2. Proces Tworzenia Planu Treści
```mermaid
sequenceDiagram
    participant U as Użytkownik
    participant F as Frontend
    participant API as Content API
    participant C as Celery
    participant AI as Gemini AI
    participant DB as Database

    U->>F: Tworzenie planu treści
    F->>API: POST /content-plans
    API->>DB: Zapisanie planu
    DB-->>API: Plan ID
    API-->>F: Plan utworzony

    U->>F: Generowanie tematów
    F->>API: POST /content-plans/{id}/generate
    API->>C: Uruchomienie zadań Celery
    API-->>F: 202 Accepted

    C->>DB: Kontekstualizacja (strategie, organizacja)
    C->>AI: Generowanie tematów blog
    AI-->>C: Lista tematów
    C->>DB: Zapisanie sugerowanych tematów
    C->>DB: Aktualizacja statusu planu

    F->>API: Sprawdzanie statusu
    API->>DB: Pobieranie tematów
    DB-->>API: Lista tematów
    API-->>F: Tematy do zatwierdzenia
```

### 3. Proces Generowania Treści AI
```mermaid
flowchart TD
    START[Rozpoczęcie Generowania] --> CONTEXT[Kontekstualizacja]
    
    CONTEXT --> GET_ORG[Pobierz Organizację]
    CONTEXT --> GET_STRATEGY[Pobierz Strategię Komunikacji]
    CONTEXT --> GET_REJECTED[Pobierz Odrzucone Tematy]
    
    GET_ORG --> BUILD_CONTEXT[Zbuduj Super-Context]
    GET_STRATEGY --> BUILD_CONTEXT
    GET_REJECTED --> BUILD_CONTEXT
    
    BUILD_CONTEXT --> RESEARCH[Wzbogacenie o Research]
    RESEARCH --> TAVILY_API[Tavily API - Trendy Branżowe]
    
    TAVILY_API --> FORMAT_PROMPT[Formatowanie Promptu]
    FORMAT_PROMPT --> GEMINI_CALL[Wywołanie Gemini API]
    
    GEMINI_CALL --> PARSE_RESPONSE[Parsowanie Odpowiedzi JSON]
    PARSE_RESPONSE --> VALIDATE[Walidacja Tematów]
    
    VALIDATE --> SAVE_TOPICS[Zapisanie do Bazy]
    SAVE_TOPICS --> UPDATE_STATUS[Aktualizacja Statusu Planu]
    
    UPDATE_STATUS --> END[Zakończenie]
    
    %% Error Handling
    GEMINI_CALL --> ERROR{Błąd API?}
    ERROR -->|Tak| FALLBACK[Tematy Fallback]
    ERROR -->|Nie| PARSE_RESPONSE
    FALLBACK --> SAVE_TOPICS
```

## Modele Danych - Relacje

```mermaid
erDiagram
    User ||--o{ Organization : "owns/belongs_to"
    User ||--o{ Task : "assigned_to"
    User ||--o{ TaskComment : "creates"
    
    Organization ||--o{ ContentPlan : "has"
    Organization ||--o{ CommunicationStrategy : "has"
    Organization ||--o{ Task : "belongs_to"
    Organization ||--o{ Project : "has"
    Organization ||--o{ Campaign : "has"
    
    ContentPlan ||--o{ SuggestedTopic : "contains"
    ContentPlan ||--o{ ScheduledPost : "schedules"
    
    SuggestedTopic ||--o{ ContentDraft : "generates"
    SuggestedTopic ||--o{ SuggestedTopic : "parent_child"
    
    ContentDraft ||--o{ ContentVariant : "has_variants"
    ContentDraft ||--o{ DraftRevision : "has_revisions"
    
    ContentVariant ||--o{ ScheduledPost : "scheduled_as"
    
    CommunicationStrategy ||--o{ Persona : "defines"
    CommunicationStrategy ||--o{ PlatformStyle : "defines"
    CommunicationStrategy ||--o{ CTARule : "defines"
    CommunicationStrategy ||--|| GeneralStyle : "has"
    
    Project ||--o{ Task : "contains"
    Project ||--o{ Campaign : "contains"
    
    Campaign ||--o{ Task : "contains"
    
    Task ||--o{ TaskComment : "has"
    Task ||--o{ TaskAttachment : "has"
```

## Stany i Przepływy Statusów

### Status Planu Treści
```mermaid
stateDiagram-v2
    [*] --> new : Utworzenie planu
    new --> generating_topics : Rozpoczęcie generowania
    generating_topics --> pending_blog_topic_approval : Tematy wygenerowane
    generating_topics --> error : Błąd generowania
    
    pending_blog_topic_approval --> generating_topics : Regeneracja tematów
    pending_blog_topic_approval --> generating_sm_topics : Zatwierdzenie tematów
    
    generating_sm_topics --> pending_final_scheduling : SM tematy wygenerowane
    generating_sm_topics --> error : Błąd generowania SM
    
    pending_final_scheduling --> complete : Harmonogram gotowy
    
    error --> new : Reset planu
    complete --> [*]
```

### Status Sugerowanych Tematów
```mermaid
stateDiagram-v2
    [*] --> suggested : Wygenerowany przez AI
    suggested --> approved : Zatwierdzony przez użytkownika
    suggested --> rejected : Odrzucony przez użytkownika
    
    approved --> [*] : Gotowy do generowania treści
    rejected --> [*] : Nie będzie używany
```

### Status Szkiców Treści
```mermaid
stateDiagram-v2
    [*] --> drafting : Rozpoczęcie generowania
    drafting --> pending_approval : Szkic wygenerowany
    drafting --> error : Błąd generowania
    
    pending_approval --> approved : Zatwierdzony
    pending_approval --> rejected : Odrzucony
    pending_approval --> needs_revision : Wymaga poprawek
    
    needs_revision --> drafting : Regeneracja z feedbackiem
    
    approved --> [*] : Gotowy do publikacji
    rejected --> [*] : Nie będzie używany
    error --> drafting : Ponowna próba
```

## Integracje Zewnętrzne

```mermaid
graph LR
    subgraph "Ada 2.0"
        CORE[Rdzeń Aplikacji]
    end
    
    subgraph "AI Services"
        GEMINI[Google Gemini API]
        TAVILY[Tavily Research API]
    end
    
    subgraph "Infrastructure"
        POSTGRES[PostgreSQL Database]
        REDIS[Redis Cache/Queue]
        DOCKER[Docker Containers]
    end
    
    subgraph "Future Integrations"
        RAGFLOW[RAGFlow - Document Processing]
        SOCIAL[Social Media APIs]
        ANALYTICS[Analytics Services]
    end
    
    CORE --> GEMINI
    CORE --> TAVILY
    CORE --> POSTGRES
    CORE --> REDIS
    
    CORE -.-> RAGFLOW
    CORE -.-> SOCIAL
    CORE -.-> ANALYTICS
    
    DOCKER --> POSTGRES
    DOCKER --> REDIS
    DOCKER --> CORE
```

## Kluczowe Funkcjonalności

### 1. **Multi-organizacyjność**
- Użytkownicy mogą należeć do wielu organizacji
- Każda organizacja ma własne strategie komunikacji
- Izolacja danych między organizacjami

### 2. **Generowanie Treści AI**
- Kontekstualizacja na podstawie strategii komunikacji
- Generowanie tematów blog i social media
- Korelacja między treściami blog a SM

### 3. **Zarządzanie Przepływem Pracy**
- Statusy planów treści i tematów
- Zatwierdzanie i odrzucanie tematów
- Regeneracja z uwzględnieniem feedbacku

### 4. **Przetwarzanie Asynchroniczne**
- Celery do długotrwałych zadań AI
- Redis jako broker kolejek
- Łańcuchy zadań dla złożonych procesów

### 5. **Elastyczna Architektura**
- Mikrousługi z FastAPI
- Separacja frontend/backend
- Konteneryzacja z Docker

Ten graf przedstawia kompletną logikę działania aplikacji Ada 2.0, od interfejsu użytkownika przez API, logikę biznesową, przetwarzanie AI, aż po bazę danych i integracje zewnętrzne.