"""FastAPI application entry point for the lead scoring backend."""

import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from .api import router as api_router
from .middleware.rate_limit import configure_rate_limiting
from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.request_limits import RequestLimitsMiddleware
from .middleware.connection_pool_monitor import ConnectionPoolMonitor
from .middleware.circuit_breaker import CircuitBreakerMiddleware
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
    if settings.environment == "production" or settings.railway_environment:
        allow_origins = [origin for origin in allow_origins if origin != "*"]
        
        # Add Railway frontend domain if not already present
        # This handles cases where ALLOWED_ORIGINS isn't set
        railway_frontend = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("FRONTEND_URL")
        if railway_frontend:
            if not railway_frontend.startswith("http"):
                railway_frontend = f"https://{railway_frontend}"
            if railway_frontend not in allow_origins:
                allow_origins.append(railway_frontend)
        
        # If still empty after processing, add common Railway patterns as fallback
        if not allow_origins:
            # Try to infer from environment or use a more permissive fallback
            logger.warning("⚠️  No CORS origins configured, using fallback")
            allow_origins = [
                "https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app",
                "http://localhost:5173",  # Local dev fallback
            ]
    
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
    """Health check endpoint with connection status and capacity metrics."""
    health_status = {
        "status": "healthy",
        "environment": settings.railway_environment or settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    # Check database connection
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        health_status["database"] = "connected"
        
        # Add connection pool metrics
        pool = engine.pool
        health_status["database_pool"] = {
            "size": pool.size(),
            "checked_in": pool.checkedin(),
            "checked_out": pool.checkedout(),
            "overflow": pool.overflow(),
            "max_overflow": getattr(pool, "_max_overflow", 0),
            "utilization_percent": round(
                ((pool.checkedout() / (pool.size() + getattr(pool, "_max_overflow", 0))) * 100)
                if (pool.size() + getattr(pool, "_max_overflow", 0)) > 0 else 0,
                2
            )
        }
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
        health_status["database_error"] = str(e)
        logger.warning(f"Database health check failed: {e}")
    
    return health_status


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


@app.get("/debug/database-url")
def debug_database_url():
    """Debug endpoint to show DATABASE_URL configuration."""
    from app.database import DATABASE_URL
    
    # Check all possible sources
    env_vars = {
        "DATABASE_URL": os.getenv("DATABASE_URL"),
        "POSTGRES_URL": os.getenv("POSTGRES_URL"),
        "PGDATABASE": os.getenv("PGDATABASE"),
        "POSTGRES_DATABASE_URL": os.getenv("POSTGRES_DATABASE_URL"),
    }
    
    # Mask sensitive parts
    def mask_url(url: str) -> str:
        if not url:
            return "not set"
        if "@" in url:
            parts = url.split("@")
            if len(parts) == 2:
                auth = parts[0]
                host = parts[1]
                if "://" in auth:
                    scheme = auth.split("://")[0]
                    masked = f"{scheme}://***:***@{host}"
                    return masked
        return url
    
    return {
        "database_url_being_used": mask_url(DATABASE_URL),
        "database_url_length": len(DATABASE_URL) if DATABASE_URL else 0,
        "is_localhost": "localhost:5433" in DATABASE_URL or "127.0.0.1:5433" in DATABASE_URL,
        "environment_variables": {k: bool(v) for k, v in env_vars.items()},
        "railway_environment": settings.railway_environment,
        "environment": settings.environment,
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
    
    # Check database connection on startup (non-blocking)
    from app.database import engine, DATABASE_URL
    if "localhost:5433" in DATABASE_URL or "127.0.0.1:5433" in DATABASE_URL:
        if settings.environment == "production" or settings.railway_environment:
            logger.warning("=" * 80)
            logger.warning("⚠️  WARNING: DATABASE_URL not configured!")
            logger.warning("=" * 80)
            logger.warning("Backend is trying to connect to localhost instead of Railway PostgreSQL.")
            logger.warning("Backend will start but database operations will fail.")
            logger.warning("")
            logger.warning("SOLUTION:")
            logger.warning("1. Go to Railway Dashboard → PostgreSQL Service")
            logger.warning("2. Click 'Connect Service' and select your Backend service")
            logger.warning("3. Railway will automatically set DATABASE_URL")
            logger.warning("")
            logger.warning("OR manually set in Backend Service → Variables:")
            logger.warning("  Name: DATABASE_URL")
            logger.warning("  Value: [Copy from PostgreSQL Service → Variables → DATABASE_URL]")
            logger.warning("=" * 80)
    
    # Test database connection (non-blocking - don't fail startup)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("✅ Database connection successful")
    except Exception as e:
        if "localhost:5433" in DATABASE_URL or "127.0.0.1:5433" in DATABASE_URL:
            logger.warning(f"⚠️  Database connection failed: {str(e)}")
            logger.warning("Backend will continue starting but database features won't work.")
            logger.warning("Connect PostgreSQL service to Backend service in Railway to fix this.")
        else:
            logger.warning(f"⚠️  Database connection failed: {str(e)}")
            logger.warning("Please check your DATABASE_URL configuration.")
        # Don't raise - allow backend to start even without database
    
    # Log all registered routes for debugging
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            logger.info(f"  {methods} {route.path}")


# Configure middleware (order matters - add security and monitoring first)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CircuitBreakerMiddleware)  # Protect against cascade failures
app.add_middleware(ConnectionPoolMonitor)    # Monitor connection pool usage
app.add_middleware(RequestLimitsMiddleware)
configure_cors(app)

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure routers
configure_routers(app)
