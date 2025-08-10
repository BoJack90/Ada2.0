# Technology Stack & Build System

## Backend Stack
- **Framework**: FastAPI (Python 3.11+) with automatic API documentation
- **Database**: PostgreSQL 15 with SQLAlchemy ORM
- **Migrations**: Alembic for database schema management
- **Task Queue**: Celery with Redis as broker for background processing
- **Cache**: Redis 7 for caching and session storage
- **AI Integration**: Google Generative AI (Gemini) for content generation
- **Authentication**: JWT tokens with python-jose and passlib for password hashing

## Frontend Stack
- **Framework**: Next.js 14+ with App Router (React 18+)
- **Language**: TypeScript with strict type checking
- **Styling**: Tailwind CSS with custom design system
- **UI Components**: Shadcn/ui components library
- **State Management**: Zustand for global state, React Query for server state
- **Forms**: React Hook Form with Zod validation
- **Animations**: Framer Motion for smooth transitions
- **Icons**: Lucide React icon library
- **Calendar**: React Big Calendar for event management

## Infrastructure & DevOps
- **Containerization**: Docker + Docker Compose for all services
- **Web Server**: Uvicorn (ASGI) for FastAPI backend
- **Development**: Hot reload enabled for both frontend and backend
- **Database**: PostgreSQL container with persistent volumes
- **Reverse Proxy**: API proxy in Next.js for Docker networking

## Development Tools
- **Backend Code Quality**: Black (formatting), Flake8 (linting), isort (import sorting)
- **Frontend Code Quality**: ESLint, Prettier, TypeScript compiler
- **Testing**: pytest for backend, Jest + React Testing Library for frontend
- **API Documentation**: Automatic Swagger/OpenAPI docs at `/docs`

## Common Commands

### Docker Development
```bash
# Start all services
docker-compose up --build

# View logs for specific service
docker-compose logs -f [web|frontend|postgres|redis|celery-worker]

# Stop all services
docker-compose down

# Rebuild containers
docker-compose up --build
```

### Database Migrations
```bash
# Create new migration
docker-compose exec web alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec web alembic upgrade head

# Check migration status
docker-compose exec web alembic current
```

### Service URLs (Development)
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8090
- **API Documentation**: http://localhost:8090/docs
- **PostgreSQL**: localhost:5432
- **Redis**: localhost:6379

### Environment Variables
- All sensitive configuration in `.env` file (not committed)
- Docker environment variables in `docker-compose.yml`
- Frontend environment variables in `frontend/.env.local`