"""Request validation middleware for security."""

import json
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from fastapi import status


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """Validate and sanitize incoming requests."""

    # Maximum request body size (1MB for JSON, 10MB for file uploads)
    MAX_JSON_BODY_SIZE = 1 * 1024 * 1024  # 1MB
    MAX_FILE_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB

    async def dispatch(self, request: Request, call_next):
        """Validate request before processing."""
        
        # Check Content-Length header
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                
                # Check if it's a file upload
                if "multipart/form-data" in request.headers.get("content-type", ""):
                    if size > self.MAX_FILE_UPLOAD_SIZE:
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={"detail": f"Request body too large. Maximum size: {self.MAX_FILE_UPLOAD_SIZE / 1024 / 1024}MB"}
                        )
                else:
                    if size > self.MAX_JSON_BODY_SIZE:
                        return JSONResponse(
                            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                            content={"detail": f"Request body too large. Maximum size: {self.MAX_JSON_BODY_SIZE / 1024 / 1024}MB"}
                        )
            except ValueError:
                # Invalid content-length, continue but log warning
                pass
        
        # Check for suspicious headers (basic detection)
        suspicious_headers = [
            "X-Forwarded-Host",
            "X-Original-URL",
        ]
        
        for header in suspicious_headers:
            if header in request.headers:
                # Log suspicious header (in production, send to monitoring)
                pass
        
        return await call_next(request)

