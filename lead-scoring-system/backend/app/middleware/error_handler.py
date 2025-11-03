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

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "detail": "Validation error",
            "errors": errors,
            "type": "validation_error",
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle HTTP exceptions."""
    logger.info(f"HTTP {exc.status_code} on {request.url.path}: {exc.detail}")

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.detail,
            "type": "http_error",
        },
    )


async def database_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle database errors."""
    logger.error(f"Database error on {request.url.path}: {exc}", exc_info=True)

    error_str = str(exc)
    
    # Check if it's a connection error indicating DATABASE_URL not set
    if "127.0.0.1" in error_str or "localhost:5433" in error_str or "Connection refused" in error_str:
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

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "type": "database_error",
        },
    )


async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all unhandled exceptions."""
    logger.error(f"Unhandled exception on {request.url.path}: {exc}", exc_info=True)

    # Don't expose internal errors in production
    if settings.environment == "production":
        detail = "An internal server error occurred. Please contact support."
    else:
        detail = f"Internal error: {str(exc)}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": detail,
            "type": "internal_error",
        },
    )

