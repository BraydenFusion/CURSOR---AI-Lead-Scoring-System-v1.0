"""FastAPI application entry point for the lead scoring backend."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError

from .api import router as api_router
from .middleware.rate_limit import configure_rate_limiting
from .middleware.error_handler import (
    database_exception_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .utils.logger import setup_logging
from .config import get_settings

settings = get_settings()

# Initialize logging
setup_logging()

app = FastAPI(title=settings.app_name, version="2.0.0", debug=settings.environment == "development")

# Configure rate limiting (optional - can be disabled in development)
try:
    if settings.environment == "production":
        configure_rate_limiting(app)
except Exception:
    # Rate limiting is optional, continue if it fails
    pass


def configure_cors(application: FastAPI) -> None:
    """Configure CORS based on environment."""

    from app.config import get_settings

    settings = get_settings()

    # In production, use configured origins; in development, allow all
    if settings.environment == "production":
        allow_origins = [origin for origin in settings.cors_origins if origin != "*"]
        if not allow_origins:
            # Fallback to localhost if misconfigured
            allow_origins = ["http://localhost:5173"]
    else:
        allow_origins = ["*"]

    application.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routers(application: FastAPI) -> None:
    """Attach API routers to the application instance."""

    application.include_router(api_router, prefix="/api")


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


# Configure middleware
configure_cors(app)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure routers
configure_routers(app)
