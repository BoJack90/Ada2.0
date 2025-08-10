# Project Structure & Organization

## Root Directory Structure
```
Ada2.0/
├── app/                    # Backend application (FastAPI)
├── frontend/              # Frontend application (Next.js)
├── migrations/            # Database migrations (Alembic)
├── tests/                 # Test files
├── docker/                # Docker configuration files
├── knx/                   # Project documentation and resources
├── docker-compose.yml     # Service orchestration
├── Dockerfile            # Backend container definition
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (not committed)
├── .gitignore           # Git ignore rules
└── rules.md             # Project development rules
```

## Backend Structure (`app/`)
```
app/
├── api/                   # API route handlers
│   ├── auth.py           # Authentication endpoints
│   ├── users.py          # User management
│   ├── organizations.py  # Organization CRUD
│   ├── tasks.py          # Task management
│   ├── projects.py       # Project management
│   ├── campaigns.py      # Campaign management
│   ├── health.py         # Health check endpoints
│   └── ai_management.py  # AI system management
├── core/                  # Core application logic
│   ├── config.py         # Application configuration
│   ├── security.py       # Authentication & authorization
│   ├── dependencies.py   # FastAPI dependencies
│   ├── prompt_manager.py # AI prompt management
│   └── ai_config_service.py # AI model configuration
├── crud/                  # Database operations
├── db/                    # Database models and connection
│   ├── database.py       # Database connection setup
│   ├── models.py         # SQLAlchemy models
│   └── schemas.py        # Pydantic schemas
├── models/                # Additional model definitions
├── schemas/               # Pydantic schema definitions
├── services/              # Business logic services
├── tasks/                 # Celery background tasks
├── publishing/            # Content publishing logic
├── main.py               # FastAPI application entry point
└── __init__.py
```

## Frontend Structure (`frontend/`)
```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── auth/         # Authentication pages
│   │   ├── organizations/ # Organization management pages
│   │   ├── api/          # API proxy routes
│   │   ├── layout.tsx    # Root layout
│   │   ├── page.tsx      # Home page
│   │   └── globals.css   # Global styles
│   ├── components/       # React components
│   │   ├── auth/         # Authentication components
│   │   ├── dashboard/    # Dashboard components
│   │   ├── layout/       # Layout components
│   │   ├── organizations/ # Organization components
│   │   ├── providers/    # Context providers
│   │   └── ui/           # Shadcn/ui components
│   ├── lib/              # Utility functions
│   │   ├── api.ts        # API client
│   │   └── utils.ts      # Helper functions
│   ├── stores/           # Zustand state stores
│   ├── styles/           # CSS files
│   └── types/            # TypeScript type definitions
├── public/               # Static assets
├── package.json          # Node.js dependencies
├── tailwind.config.js    # Tailwind CSS configuration
├── tsconfig.json         # TypeScript configuration
├── next.config.js        # Next.js configuration
└── Dockerfile           # Frontend container definition
```

## Database Structure
- **Multi-organizational architecture** with organization-scoped data
- **User-Organization relationships** with role-based access
- **Content generation system** with AI prompts and model assignments
- **Task management** with projects, campaigns, and comments
- **Communication strategies** with personas, platform styles, and rules

## Key Architectural Patterns

### Backend Patterns
- **Repository Pattern**: CRUD operations separated from business logic
- **Dependency Injection**: FastAPI dependencies for database sessions and services
- **Schema Validation**: Pydantic models for request/response validation
- **Async/Await**: Asynchronous operations throughout the application
- **Modular Routing**: Separate router files for different feature areas

### Frontend Patterns
- **Component Composition**: Reusable UI components with clear interfaces
- **State Management**: Zustand for client state, React Query for server state
- **Form Handling**: React Hook Form with Zod validation schemas
- **Layout System**: Nested layouts with App Router
- **API Abstraction**: Centralized API client with type safety

### Docker Architecture
- **Multi-container setup** with service separation
- **Health checks** for service dependencies
- **Volume persistence** for database and Redis data
- **Environment-based configuration** for different deployment stages
- **Hot reload** enabled for development workflow

## Naming Conventions
- **Files**: snake_case for Python, kebab-case for frontend files
- **Components**: PascalCase for React components
- **Variables**: camelCase for JavaScript/TypeScript, snake_case for Python
- **Database**: snake_case for table and column names
- **API Endpoints**: RESTful conventions with plural nouns