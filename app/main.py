from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.rate_limit import limiter, custom_rate_limit_handler
from slowapi.errors import RateLimitExceeded
from app.api import health, auth, users, organizations, tasks, projects, campaigns, strategy_analysis, content_plans, content_drafts, suggested_topics, content_variants, ai_management, content_workspace
from app.api.v1.endpoints import content_briefs, content_generation_control, advanced_generation
from app.db.database import create_tables
from app.core.prompt_initializer import PromptInitializer

# Create database tables
create_tables()

# Initialize AI prompts
PromptInitializer.check_and_initialize()

# Create FastAPI instance
app = FastAPI(
    title="Ada 2.0",
    description="Aplikacja marketingowa z wieloma organizacjami",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add rate limiter to app state
app.state.limiter = limiter

# Add rate limit exceeded handler
app.add_exception_handler(RateLimitExceeded, custom_rate_limit_handler)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(organizations.router, prefix="/api/v1/organizations", tags=["organizations"])
app.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
app.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
app.include_router(campaigns.router, prefix="/api/v1/campaigns", tags=["campaigns"])
app.include_router(strategy_analysis.router)
app.include_router(content_plans.router, prefix="/api/v1", tags=["content-plans"])
app.include_router(content_drafts.router, prefix="/api/v1", tags=["content-drafts"])
app.include_router(content_variants.router, prefix="/api/v1", tags=["content-variants"])
app.include_router(suggested_topics.router, prefix="/api/v1", tags=["suggested-topics"])
app.include_router(ai_management.router, prefix="/api/v1", tags=["ai-management"])
app.include_router(content_briefs.router, prefix="/api/v1", tags=["content-briefs"])
app.include_router(content_generation_control.router, prefix="/api/v1", tags=["content-generation"])
app.include_router(advanced_generation.router, tags=["advanced-generation"])
app.include_router(content_workspace.router, prefix="/api", tags=["content-workspace"])

# Import and include content plans summary router
from app.api import content_plans_summary
app.include_router(content_plans_summary.router, prefix="/api", tags=["content-plans-summary"])

# Import and include content visualization router
from app.api import content_visualization
app.include_router(content_visualization.router, prefix="/api", tags=["content-visualization"])

# Import and include Tavily status router
from app.api import tavily_status
app.include_router(tavily_status.router, tags=["tavily"])

# Test router
from app.api import test_content_plans
app.include_router(test_content_plans.router, tags=["test"])

@app.get("/")
async def root():
    """Główny endpoint aplikacji"""
    return {
        "message": "Ada 2.0 API",
        "version": "1.0.0",
        "docs": "/docs"
    }
