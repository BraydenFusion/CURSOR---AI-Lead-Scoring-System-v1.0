"""Dynamic CORS middleware that allows Railway frontend domains."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from typing import List
import logging

logger = logging.getLogger(__name__)

class DynamicCORSMiddleware(BaseHTTPMiddleware):
    """
    Enhanced CORS middleware that allows Railway frontend domains dynamically.
    Works with FastAPI's CORSMiddleware by adding Railway domain matching.
    """
    
    # Railway domain patterns
    RAILWAY_PATTERNS = [
        ".up.railway.app",
        "frontend-production",
        "frontend-production-",
    ]
    
    def __init__(self, app, allowed_origins: List[str]):
        super().__init__(app)
        self.allowed_origins = allowed_origins or []
        
    def is_railway_domain(self, origin: str) -> bool:
        """Check if origin is a Railway domain."""
        return any(pattern in origin for pattern in self.RAILWAY_PATTERNS)
    
    def is_allowed_origin(self, origin: str) -> bool:
        """Check if origin is allowed (exact match or Railway pattern)."""
        # Exact match
        if origin in self.allowed_origins:
            return True
        
        # Railway domain pattern matching
        if self.is_railway_domain(origin):
            logger.info(f"✅ Allowing Railway domain via pattern: {origin}")
            return True
        
        # Check if any allowed origin matches (case-insensitive)
        origin_lower = origin.lower()
        for allowed in self.allowed_origins:
            if origin_lower == allowed.lower():
                return True
        
        return False
    
    async def dispatch(self, request: Request, call_next):
        """Handle CORS headers dynamically."""
        origin = request.headers.get("origin")
        
        if origin and self.is_allowed_origin(origin):
            response = await call_next(request)
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
            response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH"
            response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            return response
        
        # For preflight requests
        if request.method == "OPTIONS" and origin:
            if self.is_allowed_origin(origin):
                return Response(
                    content="",
                    status_code=200,
                    headers={
                        "Access-Control-Allow-Origin": origin,
                        "Access-Control-Allow-Credentials": "true",
                        "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                        "Access-Control-Allow-Headers": "Content-Type, Authorization, X-Requested-With",
                        "Access-Control-Max-Age": "3600",
                    },
                )
        
        return await call_next(request)

