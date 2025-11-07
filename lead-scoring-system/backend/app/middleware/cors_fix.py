"""Comprehensive CORS middleware to ensure all responses include CORS headers.

This middleware runs AFTER CORS middleware to ensure CORS headers are never lost,
even if other middleware or error handlers modify responses.
"""

import re
import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Allowed origins patterns
RAILWAY_PATTERN = re.compile(r"https://.*\.up\.railway\.app|https://.*\.railway\.app")
VENTRIX_PATTERN = re.compile(r"https?://ventrix\.tech")
LOCALHOST_PATTERN = re.compile(r"http://localhost:\d+")

# Explicit allowed origins
EXPLICIT_ORIGINS = [
    "https://frontend-production-e9b2.up.railway.app",
    "https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app",
    "https://ventrix.tech",
    "http://ventrix.tech",
    "http://localhost:5173",
]


def is_origin_allowed(origin: str) -> bool:
    """Check if an origin is allowed."""
    if not origin:
        return False
    
    # Check explicit origins
    if origin in EXPLICIT_ORIGINS:
        return True
    
    # Check Railway pattern
    if RAILWAY_PATTERN.match(origin):
        return True
    
    # Check ventrix.tech pattern
    if VENTRIX_PATTERN.match(origin):
        return True
    
    # Check localhost (development)
    if LOCALHOST_PATTERN.match(origin):
        return True
    
    return False


def add_cors_headers(response: Response, origin: str | None) -> None:
    """Add CORS headers to response."""
    if origin and is_origin_allowed(origin):
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        # Fallback: allow all origins if no origin specified (less secure but ensures CORS works)
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    # Always add these headers
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    response.headers["Access-Control-Expose-Headers"] = "*"
    response.headers["Access-Control-Max-Age"] = "3600"


class CORSFixMiddleware(BaseHTTPMiddleware):
    """Middleware to ensure CORS headers are always present on all responses."""
    
    async def dispatch(self, request: Request, call_next):
        origin = request.headers.get("origin")
        
        # Handle OPTIONS preflight requests
        if request.method == "OPTIONS":
            response = Response()
            add_cors_headers(response, origin)
            logger.info(f"✅ OPTIONS preflight handled for {request.url.path} from {origin}")
            return response
        
        # Process the request
        response = await call_next(request)
        
        # Ensure CORS headers are present (even if other middleware removed them)
        add_cors_headers(response, origin)
        
        return response

