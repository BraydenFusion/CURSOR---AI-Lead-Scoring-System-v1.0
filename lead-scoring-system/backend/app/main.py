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
import logging

from .utils.logger import setup_logging
from .config import get_settings

settings = get_settings()

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    debug=settings.environment == "development"
)

# Configure rate limiting (optional - can be disabled in development)
try:
    if settings.environment == "production":
        configure_rate_limiting(app)
except Exception:
    # Rate limiting is optional, continue if it fails
    pass


def configure_cors(application: FastAPI) -> None:
    """Configure CORS based on environment."""

    # Use settings for allowed origins (handles Railway environment)
    allow_origins = settings.cors_origins
    
    # In development, allow all if no specific origins set
    if settings.environment != "production" and not allow_origins:
        allow_origins = ["*"]
    
    # Filter out wildcard in production
    if settings.environment == "production":
        allow_origins = [origin for origin in allow_origins if origin != "*"]
        if not allow_origins:
            # Fallback to localhost if misconfigured
            allow_origins = ["http://localhost:5173"]
    
    logger.info(f"CORS allowed origins: {allow_origins}")

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


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"{settings.app_name} v2.0",
        "status": "operational",
        "environment": settings.railway_environment or settings.environment
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "environment": settings.railway_environment or settings.environment
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Environment: {settings.railway_environment or settings.environment}")
    logger.info(f"Debug mode: {settings.environment == 'development'}")
    logger.info(f"Port: {settings.port}")


# Configure middleware
configure_cors(app)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure routers
configure_routers(app)
