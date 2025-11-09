"""FastAPI application entry point for the lead scoring backend."""

import os
from datetime import datetime
import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from starlette.exceptions import HTTPException as StarletteHTTPException

from .api import router as api_router
from .cache import redis_client
from .config import get_settings
from .middleware.circuit_breaker import CircuitBreakerMiddleware
from .middleware.connection_pool_monitor import ConnectionPoolMonitor
from .middleware.cors_fix import CORSFixMiddleware
from .middleware.error_handler import (
    database_exception_handler,
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)
from .middleware.rate_limit import configure_rate_limiting
from .middleware.request_limits import RequestLimitsMiddleware
from .middleware.request_validation import RequestValidationMiddleware
from .middleware.security_headers import SecurityHeadersMiddleware
from .tasks.crm_scheduler import start_crm_sync_scheduler
from .tasks.email_scheduler import start_email_sync_scheduler
from .utils.logger import setup_logging

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


# Store CORS origins globally for OPTIONS handler
_cors_allow_origins = []

def configure_cors(application: FastAPI) -> None:
    """Configure CORS based on environment - ALWAYS allows Railway frontend domains."""
    global _cors_allow_origins

    # Start with settings or defaults
    allow_origins = list(settings.cors_origins) if settings.cors_origins else []
    
    # CRITICAL: Always add Railway frontend domain explicitly
    railway_frontend_domains = [
        "https://frontend-production-e9b2.up.railway.app",
        "https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app",
        "https://ventrix.tech",  # Production domain
        "http://ventrix.tech",  # Allow HTTP for redirects
        "https://www.ventrix.tech",
        "http://www.ventrix.tech",
        "https://app.ventrix.tech",
        "http://app.ventrix.tech",
    ]
    
    # Add from environment if available
    railway_frontend = os.getenv("RAILWAY_PUBLIC_DOMAIN") or os.getenv("FRONTEND_URL")
    if railway_frontend:
        if not railway_frontend.startswith("http"):
            railway_frontend = f"https://{railway_frontend}"
        if railway_frontend not in railway_frontend_domains:
            railway_frontend_domains.append(railway_frontend)
    
    # Always add Railway frontend domains (remove wildcards and duplicates)
    for domain in railway_frontend_domains:
        if domain not in allow_origins:
            allow_origins.append(domain)
    
    # Remove wildcards in production
    if settings.environment == "production" or settings.railway_environment:
        allow_origins = [origin for origin in allow_origins if origin != "*"]
    
    # Add localhost for development
    if settings.environment != "production":
        if "http://localhost:5173" not in allow_origins:
            allow_origins.append("http://localhost:5173")
    
    # Store globally for OPTIONS handler
    _cors_allow_origins = allow_origins.copy()
    
    logger.info(f"🌐 CORS Configuration:")
    logger.info(f"   Allowed origins: {allow_origins}")
    logger.info(
        "   Regex pattern: https://.*\\.up\\.railway\\.app|https://.*\\.railway\\.app|https?://(?:[\\w-]+\\.)?ventrix\\.tech"
    )
    
    # Use FastAPI's built-in CORS middleware
    # CRITICAL: Use both explicit origins AND regex pattern for Railway
    # CRITICAL: allow_origin_regex takes precedence over allow_origins for matching
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins if allow_origins else ["*"],  # Explicit origins (fallback to all in dev)
        allow_origin_regex=r"https://.*\.up\.railway\.app|https://.*\.railway\.app|https?://(?:[\w-]+\.)?ventrix\.tech",  # Allow ALL Railway domains and ventrix.tech via regex
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=3600,  # Cache preflight for 1 hour
    )
    
    logger.info("✅ CORS middleware configured and added to application")


def configure_routers(application: FastAPI) -> None:
    """Attach API routers to the application instance."""

    @application.get("/api")
    def api_info():
        """API information endpoint."""
        return {
            "message": "Lead Scoring System API",
            "version": "2.0.0",
            "endpoints": {
                "authentication": "/api/auth",
                "leads": "/api/leads",
                "assignments": "/api/assignments",
                "notes": "/api/notes",
                "notifications": "/api/notifications",
                "health": "/health",
                "docs": "/docs",
                "openapi": "/openapi.json"
            },
            "base_path": "/api"
        }

    @application.get("/api/config")
    def frontend_config(request: Request):
        """Frontend configuration endpoint - provides API base URL."""
        import os
        
        # Get backend URL from request (most reliable)
        scheme = request.url.scheme
        host = request.url.hostname
        port = request.url.port
        
        # Construct base URL
        if port and port not in [80, 443]:
            backend_base = f"{scheme}://{host}:{port}"
        else:
            backend_base = f"{scheme}://{host}"
        
        api_base_url = f"{backend_base}/api"
        
        # Get CORS origins for debugging
        cors_origins = settings.cors_origins
        
        return {
            "apiBaseUrl": api_base_url,
            "environment": settings.railway_environment or settings.environment,
            "corsOrigins": cors_origins,
            "frontendOrigin": request.headers.get("origin"),
        }
    
    @application.options("/api/{path:path}")
    async def options_handler(request: Request, path: str):
        """Explicit OPTIONS handler for CORS preflight."""
        import re
        origin = request.headers.get("origin")
        logger.info(f"🔍 OPTIONS preflight for /api/{path} from origin: {origin}")
        
        # Check if origin is allowed (same logic as CORS middleware)
        allowed_origin = None
        if origin:
            # Check against explicit origins (use global variable)
            if origin in _cors_allow_origins:
                allowed_origin = origin
                logger.info(f"✅ Origin allowed (explicit): {origin}")
            # Check against regex pattern for Railway and ventrix.tech
            elif re.match(r"https://.*\.up\.railway\.app|https://.*\.railway\.app|https?://(?:[\w-]+\.)?ventrix\.tech", origin):
                allowed_origin = origin
                logger.info(f"✅ Origin allowed (regex): {origin}")
            else:
                logger.warning(f"⚠️  Origin not allowed: {origin}")
        
        # Use origin if allowed, otherwise use * (for development)
        cors_origin = allowed_origin if allowed_origin else (origin if origin else "*")
        
        logger.info(f"📤 Sending CORS headers with origin: {cors_origin}")
        
        return JSONResponse(
            content={"message": "CORS preflight"},
            headers={
                "Access-Control-Allow-Origin": cors_origin,
                "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Credentials": "true",
                "Access-Control-Max-Age": "3600",
            }
        )

    application.include_router(api_router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": f"{settings.app_name} v2.0",
        "status": "operational",
        "environment": settings.railway_environment or settings.environment
    }


def check_database() -> str:
    """Return database connectivity status."""
    try:
        from app.database import engine
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return "connected"
    except Exception as exc:  # pragma: no cover - network/resource dependent
        logger.warning("Database health check failed: %s", exc)
        return "disconnected"


def check_redis() -> str:
    """Return Redis connectivity status."""
    try:
        redis_client.ping()
        return "connected"
    except Exception as exc:  # pragma: no cover - network/resource dependent
        logger.warning("Redis health check failed: %s", exc)
        return "disconnected"


def collect_health_data() -> dict:
    """Gather current metrics about system health."""
    data: dict = {
        "status": "healthy",
        "environment": settings.railway_environment or settings.environment,
        "timestamp": datetime.utcnow().isoformat(),
    }

    try:
        from app.database import engine

        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))

        pool = engine.pool
        data["database"] = {
            "status": "connected",
            "pool": {
                "size": getattr(pool, "size", lambda: 0)(),
                "checked_in": getattr(pool, "checkedin", lambda: 0)(),
                "checked_out": getattr(pool, "checkedout", lambda: 0)(),
                "overflow": getattr(pool, "overflow", lambda: 0)(),
                "max_overflow": getattr(pool, "_max_overflow", 0),
            },
        }
    except Exception as exc:  # pragma: no cover - relies on environment
        data["database"] = {"status": "disconnected", "error": str(exc)}
        data["status"] = "degraded"

    try:
        info = redis_client.info()
        data["redis"] = {
            "status": "connected",
            "connected_clients": info.get("connected_clients"),
            "uptime": info.get("uptime_in_seconds"),
            "memory": info.get("used_memory_human") or info.get("used_memory"),
            "ops_per_sec": info.get("instantaneous_ops_per_sec"),
        }
    except Exception as exc:  # pragma: no cover - relies on environment
        data["redis"] = {"status": "disconnected", "error": str(exc)}
        data["status"] = "degraded"

    return data


@app.get("/health", response_class=HTMLResponse)
def health_dashboard():
    data = collect_health_data()
    return HTMLResponse(content=render_health_dashboard(data))


@app.get("/health.json")
def health_json():
    return JSONResponse(content=collect_health_data())


def generate_health_dashboard(health_data: dict) -> str:
    """Deprecated wrapper for legacy imports; kept for compatibility."""
    return render_health_dashboard(health_data)


def render_health_dashboard(health_data: dict) -> str:
    """Render the refreshed health dashboard."""
    status = (health_data.get("status") or "unknown").upper()
    database = health_data.get("database") or {}
    redis_info = health_data.get("redis") or {}
    environment = health_data.get("environment") or "unknown"
    timestamp = health_data.get("timestamp") or ""
    pool = database.get("pool") or {}

    pool_size = pool.get("size") or 0
    checked_out = pool.get("checked_out") or 0
    max_overflow = pool.get("max_overflow") or 0
    total_capacity = pool_size + max_overflow if pool_size or max_overflow else 0
    utilization = round((checked_out / total_capacity) * 100, 2) if total_capacity else 0.0

    initial_payload = json.dumps(health_data)

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>LeadScore AI • Health Center</title>
    <style>
        :root {{
            --navy-dark: #050d1f;
            --navy: #0b1f3a;
            --navy-light: #132c54;
            --background: #f3f5fb;
            --white: #ffffff;
            --success: #06d6a0;
            --warning: #f6ad55;
            --danger: #f26464;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            margin: 0;
            font-family: "Inter", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
            background: var(--navy-dark);
            color: var(--navy);
        }}

        header {{
            padding: 36px 6vw 28px;
            background: var(--navy);
            color: var(--white);
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3);
        }}

        header h1 {{
            margin: 0 0 8px;
            font-size: 34px;
            font-weight: 700;
        }}

        header p {{
            margin: 0;
            color: rgba(255, 255, 255, 0.7);
            font-size: 15px;
        }}

        main {{
            background: var(--background);
            padding: 32px 6vw 48px;
            min-height: calc(100vh - 140px);
        }}

        .grid {{
            display: grid;
            gap: 24px;
        }}

        .grid-3 {{
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        }}

        .grid-2 {{
            grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
        }}

        .card {{
            background: var(--white);
            border-radius: 20px;
            padding: 24px;
            box-shadow: 0 16px 40px rgba(11, 31, 58, 0.08);
        }}

        .card h2 {{
            margin: 0 0 12px;
            font-size: 15px;
            letter-spacing: 0.12em;
            font-weight: 600;
            color: var(--navy-light);
            text-transform: uppercase;
        }}

        .metric {{
            font-size: 32px;
            font-weight: 700;
            margin-bottom: 6px;
            color: var(--navy);
        }}

        .meta {{
            font-size: 13px;
            color: rgba(11, 31, 58, 0.6);
        }}

        .status-chip {{
            display: inline-flex;
            align-items: center;
            padding: 8px 14px;
            border-radius: 999px;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 0.18em;
        }}

        .status-chip.HEALTHY {{
            background: rgba(6, 214, 160, 0.2);
            color: var(--success);
        }}

        .status-chip.DEGRADED {{
            background: rgba(246, 173, 85, 0.24);
            color: #c05621;
        }}

        .status-chip.DISCONNECTED {{
            background: rgba(242, 100, 100, 0.24);
            color: var(--danger);
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            font-size: 14px;
        }}

        th {{
            text-align: left;
            padding: 6px 0;
            color: rgba(11, 31, 58, 0.6);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}

        td {{
            padding: 6px 0;
            color: rgba(11, 31, 58, 0.82);
        }}

        .footer {{
            margin-top: 32px;
            text-align: center;
            font-size: 13px;
            color: rgba(11, 31, 58, 0.55);
        }}
    </style>
</head>
<body>
    <header>
        <h1>LeadScore AI — Health Center</h1>
        <p>Live operational status for your Railway deployment.</p>
    </header>
    <main>
        <div class="grid grid-3">
            <div class="card">
                <h2>System Status</h2>
                <div id="system-chip" class="status-chip {status}">{status}</div>
                <div class="meta" id="timestamp-value">Updated {timestamp}</div>
            </div>
            <div class="card">
                <h2>Environment</h2>
                <div class="metric" id="environment-value">{environment}</div>
                <div class="meta">Railway environment</div>
            </div>
            <div class="card">
                <h2>Database Utilization</h2>
                <div class="metric" id="db-utilization">{utilization}%</div>
                <div class="meta" id="db-connections">
                    Active connections: {checked_out} / {pool_size}
                </div>
            </div>
        </div>

        <div class="grid grid-2" style="margin-top: 24px;">
            <div class="card">
                <h2>Database</h2>
                <div id="db-chip" class="status-chip {(database.get('status') or 'unknown').upper()}">{(database.get('status') or 'unknown').upper()}</div>
                <table style="margin-top: 12px;">
                    <tr><th>Checked In</th><td id="db-checked-in">{pool.get('checked_in', 0)}</td></tr>
                    <tr><th>Checked Out</th><td id="db-checked-out">{pool.get('checked_out', 0)}</td></tr>
                    <tr><th>Overflow</th><td id="db-overflow">{pool.get('overflow', 0)}</td></tr>
                    <tr><th>Error</th><td id="db-error">{database.get('error', '')}</td></tr>
                </table>
            </div>
            <div class="card">
                <h2>Redis Cache</h2>
                <div id="redis-chip" class="status-chip {(redis_info.get('status') or 'unknown').upper()}">{(redis_info.get('status') or 'unknown').upper()}</div>
                <table style="margin-top: 12px;">
                    <tr><th>Clients</th><td id="redis-clients">{redis_info.get('connected_clients', '--')}</td></tr>
                    <tr><th>Ops / sec</th><td id="redis-ops">{redis_info.get('ops_per_sec', '--')}</td></tr>
                    <tr><th>Memory</th><td id="redis-memory">{redis_info.get('memory', '--')}</td></tr>
                    <tr><th>Error</th><td id="redis-error">{redis_info.get('error', '')}</td></tr>
                </table>
            </div>
        </div>

        <div class="footer">Dashboard auto-refreshes every 10 seconds.</div>
    </main>

    <script type="application/json" id="health-data">{initial_payload}</script>
    <script>
        const dataElement = document.getElementById("health-data");

        function applyStatusChip(id, status) {{
            const el = document.getElementById(id);
            if (!el) return;
            el.textContent = status;
            el.className = "status-chip " + status;
        }}

        function updateUI(data) {{
            const status = (data.status || "unknown").toUpperCase();
            const db = data.database || {{}};
            const pool = db.pool || {{}};
            const redis = data.redis || {{}};

            const poolSize = pool.size || 0;
            const checkedOut = pool.checked_out || 0;
            const maxOverflow = pool.max_overflow || 0;
            const total = poolSize + maxOverflow;
            const utilization = total ? Math.round((checkedOut / total) * 100) : 0;

            applyStatusChip("system-chip", status);
            document.getElementById("timestamp-value").textContent =
                "Updated " + new Date(data.timestamp || Date.now()).toLocaleString();
            document.getElementById("environment-value").textContent = data.environment || "unknown";
            document.getElementById("db-utilization").textContent = utilization + "%";
            document.getElementById("db-connections").textContent =
                `Active connections: ${pool.checked_out || 0} / ${pool.size || 0}`;

            const dbStatus = (db.status || "unknown").toUpperCase();
            applyStatusChip("db-chip", dbStatus);
            document.getElementById("db-checked-in").textContent = pool.checked_in ?? 0;
            document.getElementById("db-checked-out").textContent = pool.checked_out ?? 0;
            document.getElementById("db-overflow").textContent = pool.overflow ?? 0;
            document.getElementById("db-error").textContent = db.error || "";

            const redisStatus = (redis.status || "unknown").toUpperCase();
            applyStatusChip("redis-chip", redisStatus);
            document.getElementById("redis-clients").textContent = redis.connected_clients ?? "--";
            document.getElementById("redis-ops").textContent = redis.ops_per_sec ?? "--";
            document.getElementById("redis-memory").textContent = redis.memory ?? "--";
            document.getElementById("redis-error").textContent = redis.error || "";
        }}

        async function refresh() {{
            try {{
                const response = await fetch("/health.json", {{ cache: "no-store" }});
                if (!response.ok) return;
                const data = await response.json();
                updateUI(data);
            }} catch (err) {{
                console.warn("Health refresh failed", err);
            }}
        }}

        updateUI(JSON.parse(dataElement.textContent));
        setInterval(refresh, 10000);
    </script>
</body>
</html>"""
    
    return html


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
        error_str = str(e)
        if "localhost:5433" in DATABASE_URL or "127.0.0.1:5433" in DATABASE_URL:
            logger.warning(f"⚠️  Database connection failed: {error_str}")
            logger.warning("Backend will continue starting but database features won't work.")
            logger.warning("Connect PostgreSQL service to Backend service in Railway to fix this.")
        elif "Name or service not known" in error_str or "[Errno -2]" in error_str:
            logger.error("=" * 80)
            logger.error("⚠️  DATABASE DNS RESOLUTION FAILURE")
            logger.error("=" * 80)
            logger.error(f"Error: {error_str}")
            logger.error("")
            logger.error("CAUSE: DATABASE_URL hostname cannot be resolved")
            logger.error("")
            logger.error("SOLUTION:")
            logger.error("1. Railway Dashboard → PostgreSQL Service → Variables")
            logger.error("2. Copy DATABASE_URL value (full URL, not ${{ references})")
            logger.error("3. Railway Dashboard → Backend Service → Variables")
            logger.error("4. Set DATABASE_URL = [paste the actual URL]")
            logger.error("5. Ensure no ${{ Postgres.DATABASE_URL }} syntax")
            logger.error("6. Redeploy backend service")
            logger.error("=" * 80)
        else:
            logger.warning(f"⚠️  Database connection failed: {error_str}")
            logger.warning("Please check your DATABASE_URL configuration.")
        # Don't raise - allow backend to start even without database
    
    # Log all registered routes for debugging
    logger.info("Registered routes:")
    for route in app.routes:
        if hasattr(route, 'path'):
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            logger.info(f"  {methods} {route.path}")
    
    # Verify auth routes are registered
    auth_routes = [r for r in app.routes if hasattr(r, 'path') and '/auth' in r.path]
    if auth_routes:
        logger.info(f"✅ Auth routes registered: {len(auth_routes)} routes")
        for route in auth_routes[:5]:  # Show first 5
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            logger.info(f"  Auth route: {methods} {route.path}")
    else:
        logger.error("❌ No auth routes found! This will cause 404 errors on login.")
    
    # Verify login route specifically
    login_routes = [r for r in app.routes if hasattr(r, 'path') and '/login' in r.path]
    if login_routes:
        logger.info(f"✅ Login route found:")
        for route in login_routes:
            methods = list(route.methods) if hasattr(route, 'methods') and route.methods else []
            logger.info(f"  Login: {methods} {route.path}")
    else:
        logger.error("❌ Login route not found! Check auth router registration.")


# Configure middleware (order matters - add security and monitoring first)
# IMPORTANT: CORS must be added BEFORE SecurityHeadersMiddleware to avoid conflicts
configure_cors(app)  # CORS first - before other middleware
app.add_middleware(CORSFixMiddleware)  # CORS fix - ensures headers are never lost (runs AFTER CORS)
app.add_middleware(RequestValidationMiddleware)  # Validate requests first
app.add_middleware(SecurityHeadersMiddleware)  # Security headers
app.add_middleware(CircuitBreakerMiddleware)  # Protect against cascade failures
app.add_middleware(ConnectionPoolMonitor)    # Monitor connection pool usage
app.add_middleware(RequestLimitsMiddleware)  # Request size limits

# Register exception handlers
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, global_exception_handler)

# Configure routers
configure_routers(app)
start_email_sync_scheduler(app)
start_crm_sync_scheduler(app)
