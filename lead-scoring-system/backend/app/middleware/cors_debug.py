"""CORS debugging middleware to log and verify CORS headers."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

logger = logging.getLogger(__name__)


class CORSDebugMiddleware(BaseHTTPMiddleware):
    """Middleware to debug CORS issues."""
    
    async def dispatch(self, request: Request, call_next):
        """Log CORS-related information."""
        origin = request.headers.get("origin")
        method = request.method
        
        # Log incoming request
        if origin:
            logger.info(f"🌐 CORS Request: {method} {request.url.path} from origin: {origin}")
        
        # Handle preflight OPTIONS requests
        if method == "OPTIONS":
            logger.info(f"🔍 OPTIONS preflight request from: {origin}")
        
        response = await call_next(request)
        
        # Log response headers
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-credentials": response.headers.get("access-control-allow-credentials"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
            "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
        }
        
        if origin:
            logger.info(f"📤 CORS Response Headers: {cors_headers}")
        
        return response

