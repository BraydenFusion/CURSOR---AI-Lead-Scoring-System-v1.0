"""Security headers middleware for production security."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # CRITICAL: Never overwrite CORS headers - preserve them if they exist
        # CORS headers are set by CORSFixMiddleware and must not be removed
        
        # Content Security Policy - Allow same origin and trusted sources
        # Adjust as needed for your frontend domain
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # unsafe-eval for Swagger UI
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none';"
        )
        
        # Security headers - adjust for docs pages
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            # Less restrictive for Swagger UI/ReDoc
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "SAMEORIGIN"  # Allow same-origin framing for docs
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            # Don't set Permissions-Policy for docs (may interfere with Swagger UI)
        else:
            # Full security headers for other endpoints
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
            response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # Only add CSP and HSTS in production (to avoid breaking Swagger UI in dev)
        if request.url.path.startswith("/docs") or request.url.path.startswith("/redoc"):
            # More permissive CSP for Swagger UI/ReDoc - they need to load external resources
            # Swagger UI loads from CDNs and needs to fetch the OpenAPI schema
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://unpkg.com; "
                "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://unpkg.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://fonts.gstatic.com; "
                "connect-src 'self' https:; "
                "frame-ancestors 'none';"
            )
        else:
            response.headers["Content-Security-Policy"] = csp
        
        # HSTS - Only in production with HTTPS
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response

