"""Rate limiting middleware for API endpoints."""

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request, HTTPException


# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


def configure_rate_limiting(app):
    """Configure rate limiting for the FastAPI app."""
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    return app


# Rate limit decorators for different endpoints
rate_limit_strict = limiter.limit("10/minute")  # Strict limits for auth
rate_limit_normal = limiter.limit("100/minute")  # Normal API limits
rate_limit_generous = limiter.limit("1000/hour")  # For read-heavy endpoints

