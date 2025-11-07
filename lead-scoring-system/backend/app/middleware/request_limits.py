"""Request size and timeout limits middleware."""

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
import logging

logger = logging.getLogger(__name__)

# Maximum request body size: 1MB (1,048,576 bytes)
MAX_REQUEST_SIZE = 1024 * 1024


class RequestLimitsMiddleware(BaseHTTPMiddleware):
    """Enforce request size limits and handle oversized requests."""

    async def dispatch(self, request: Request, call_next):
        # Check Content-Length header if present
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    logger.warning(
                        f"Request too large: {size} bytes from {request.client.host if request.client else 'unknown'}"
                    )
                    origin = request.headers.get("origin")
                    response = JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={
                            "detail": f"Request body too large. Maximum size: {MAX_REQUEST_SIZE // 1024}KB",
                            "type": "request_too_large",
                            "max_size_kb": MAX_REQUEST_SIZE // 1024,
                        },
                    )
                    # Add CORS headers to error response
                    if origin:
                        response.headers["Access-Control-Allow-Origin"] = origin
                        response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
                    response.headers["Access-Control-Allow-Headers"] = "*"
                    return response
            except ValueError:
                # Invalid content-length header, let it through
                pass

        response = await call_next(request)
        return response

