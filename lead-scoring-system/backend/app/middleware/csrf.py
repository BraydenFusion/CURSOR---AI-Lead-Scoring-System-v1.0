"""CSRF protection middleware."""

import secrets
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import status


class CSRFProtectionMiddleware(BaseHTTPMiddleware):
    """CSRF protection for state-changing operations."""

    # Safe HTTP methods that don't require CSRF protection
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        """Check CSRF token for state-changing requests."""
        
        # Skip CSRF check for safe methods
        if request.method in self.SAFE_METHODS:
            return await call_next(request)
        
        # Skip CSRF check for API endpoints that use JWT (already authenticated)
        # CSRF is primarily for session-based auth, but we add it for extra security
        if request.url.path.startswith("/api/"):
            # For API endpoints, we rely on JWT token validation
            # But we can add CSRF token check for forms if needed
            return await call_next(request)
        
        # For other endpoints, check CSRF token
        # This is a simplified implementation - enhance based on your needs
        csrf_token = request.headers.get("X-CSRF-Token")
        expected_token = request.cookies.get("csrf_token")
        
        if csrf_token != expected_token:
            # Generate new token for GET requests
            if request.method == "GET":
                response = await call_next(request)
                new_token = secrets.token_hex(32)
                response.set_cookie(
                    "csrf_token",
                    new_token,
                    httponly=True,
                    samesite="strict",
                    secure=True  # Only over HTTPS
                )
                return response
            else:
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "CSRF token validation failed"}
                )
        
        return await call_next(request)

