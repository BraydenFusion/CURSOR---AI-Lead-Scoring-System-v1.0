"""Global exception handlers for the application."""

import logging
from typing import Any

from fastapi import Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def _add_cors_headers(response: JSONResponse, request: Request) -> JSONResponse:
    """Add CORS headers to response to ensure frontend can read error messages."""
    origin = request.headers.get("origin")
    if origin:
        # Check if origin is allowed (Railway domains)
        if origin.endswith(".up.railway.app") or origin.endswith(".railway.app"):
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
        elif origin == "http://localhost:5173":
            response.headers["Access-Control-Allow-Origin"] = origin
            response.headers["Access-Control-Allow-Credentials"] = "true"
    else:
        # Fallback: allow all origins for error responses (less secure but ensures CORS works)
        response.headers["Access-Control-Allow-Origin"] = "*"
    
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    errors = []
    for error in exc.errors():
        field_path = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(
            {
                "field": field_path,
                "message": error["msg"],
                "type": error["type"],
            }
        )

    logger.warning(f"Validation error on {request.url.path}: {errors}")

    response = JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "type": "validation_error",
        },
    )
    return _add_cors_headers(response, request)


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.info(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    response = JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error",
        },
    )
    return _add_cors_headers(response, request)


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)

    error_str = str(exc)
    
    # Check for DNS resolution failure (Name or service not known)
    if "Name or service not known" in error_str or "[Errno -2]" in error_str:
        detail = (
            "Database DNS resolution error: Cannot resolve database hostname. "
            "The DATABASE_URL hostname is invalid or unreachable. "
            "SOLUTION: Check Railway Backend → Variables → DATABASE_URL. "
            "Copy the actual URL from PostgreSQL → Variables (not ${{ references})."
        )
        logger.error("⚠️  DNS resolution failure - DATABASE_URL hostname cannot be resolved")
        logger.error("⚠️  This usually means DATABASE_URL contains an invalid/unresolvable hostname")
        logger.error("⚠️  Or Railway variable references (${{ }}) are not resolving")
    
    # Check if it's a connection error indicating DATABASE_URL not set
    elif "127.0.0.1" in error_str or "localhost:5433" in error_str or "Connection refused" in error_str:
        detail = (
            "Database connection error: Backend cannot connect to database. "
            "Please ensure PostgreSQL service is connected to backend service in Railway, "
            "or DATABASE_URL environment variable is set correctly."
        )
        logger.error("⚠️  DATABASE_URL appears to not be set - backend is using localhost default")
    elif settings.environment == "production":
        detail = "A database error occurred. Please try again later."
    else:
        detail = f"Database error: {error_str}"

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "type": "database_error",
        },
    )
    return _add_cors_headers(response, request)


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    # Check for specific password-related errors
    error_str = str(exc)
    if "password cannot be longer than 72 bytes" in error_str:
        detail = (
            "Password validation error: Password is too long. "
            "Please use a password that is 72 characters or less when encoded."
        )
        logger.error("⚠️  Password length error - password exceeds bcrypt's 72-byte limit")
    # Don't expose internal errors in production
    elif settings.environment == "production":
        detail = "An internal server error occurred. Please contact support."
    else:
        detail = f"Internal error: {str(exc)}"

    response = JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "type": "internal_error",
        },
    )
    return _add_cors_headers(response, request)

