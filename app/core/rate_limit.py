from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, Response
from fastapi.responses import JSONResponse
import time

# Create limiter instance
limiter = Limiter(key_func=get_remote_address)

# Custom rate limit handler
async def custom_rate_limit_handler(request: Request, exc: RateLimitExceeded) -> Response:
    response = JSONResponse(
        content={
            "detail": f"Rate limit exceeded: {exc.detail}",
            "error": "rate_limit_exceeded"
        },
        status_code=429,
    )
    response.headers["Retry-After"] = str(60)  # Tell client to retry after 60 seconds
    return response

# Rate limit configurations for different endpoints
RATE_LIMITS = {
    "default": "100/minute",
    "auth": "5/minute",
    "upload": "10/minute",
    "api_heavy": "30/minute",
}

# Decorator for rate limiting
def rate_limit(limit: str = RATE_LIMITS["default"]):
    """
    Apply rate limiting to an endpoint
    
    Args:
        limit: Rate limit string (e.g., "5/minute", "100/hour")
    """
    return limiter.limit(limit)