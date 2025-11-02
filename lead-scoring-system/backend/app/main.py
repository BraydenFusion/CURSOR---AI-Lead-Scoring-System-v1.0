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

# Always enable docs, even in production (for Railway deployment)
# If you want to disable in production, set docs_url=None conditionally
app = FastAPI(
    title=settings.app_name,
    version="2.0.0",
    debug=settings.environment == "development",
    docs_url="/docs",  # Explicitly enable Swagger UI
    redoc_url="/redoc",  # Explicitly enable ReDoc
    openapi_url="/openapi.json"  # Explicitly enable OpenAPI schema
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


@app.get("/test")
def test_endpoint():
    """Simple test endpoint to verify routing."""
    return {"message": "Test endpoint works!", "status": "ok"}


@app.get("/docs-alias")
def docs_alias():
    """Alternative endpoint that redirects to docs."""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/docs")


@app.get("/api/openapi.json")
def openapi_json_alias():
    """Alternative OpenAPI endpoint."""
    return app.openapi()


@app.get("/debug/routes")
def debug_routes():
    """Debug endpoint to list all available routes."""
    routes = []
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            route_info = {
                "path": route.path,
                "methods": methods,
                "name": getattr(route, 'name', 'unknown')
            }
            routes.append(route_info)
    return {
        "routes": routes,
        "total": len(routes),
        "docs_enabled": app.docs_url is not None,
        "redoc_enabled": app.redoc_url is not None
    }


@app.on_event("startup")
async def startup_event():
    """Startup event handler."""
    logger.info(f"Starting {settings.app_name}")
    logger.info(f"Environment: {settings.railway_environment or settings.environment}")
    logger.info(f"Debug mode: {settings.environment == 'development'}")
    logger.info(f"Port: {settings.port}")
    logger.info(f"API docs available at: {app.docs_url}")
    logger.info(f"ReDoc available at: {app.redoc_url}")
    logger.info(f"OpenAPI schema available at: {app.openapi_url}")
    
    # Log all registered routes for debugging
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            logger.info(f"  {methods} {route.path}")


# Configure middleware
configure_cors(app)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure routers
configure_routers(app)
