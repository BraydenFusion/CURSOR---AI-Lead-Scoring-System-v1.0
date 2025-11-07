"""FastAPI application entry point for the lead scoring backend."""

import os
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text

from .api import router as api_router
from .middleware.rate_limit import configure_rate_limiting
from .middleware.security_headers import SecurityHeadersMiddleware
from .middleware.request_limits import RequestLimitsMiddleware
from .middleware.request_validation import RequestValidationMiddleware
from .middleware.connection_pool_monitor import ConnectionPoolMonitor
from .middleware.circuit_breaker import CircuitBreakerMiddleware
from .middleware.cors_fix import CORSFixMiddleware
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
    logger.info(f"   Regex pattern: https://.*\\.up\\.railway\\.app|https://.*\\.railway\\.app|https?://ventrix\\.tech")
    
    # Use FastAPI's built-in CORS middleware
    # CRITICAL: Use both explicit origins AND regex pattern for Railway
    # CRITICAL: allow_origin_regex takes precedence over allow_origins for matching
    application.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins if allow_origins else ["*"],  # Explicit origins (fallback to all in dev)
        allow_origin_regex=r"https://.*\.up\.railway\.app|https://.*\.railway\.app|https?://ventrix\.tech",  # Allow ALL Railway domains and ventrix.tech via regex
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
            elif re.match(r"https://.*\.up\.railway\.app|https://.*\.railway\.app|https?://ventrix\.tech", origin):
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


async def get_health_data():
    """Get health status data."""
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
        max_overflow = getattr(pool, "_max_overflow", 0)
        pool_size = pool.size()
        checked_in = pool.checkedin()
        checked_out = pool.checkedout()
        overflow = pool.overflow()
        total_available = pool_size + max_overflow
        
        health_status["database_pool"] = {
            "size": pool_size,
            "checked_in": checked_in,
            "checked_out": checked_out,
            "overflow": overflow,
            "max_overflow": max_overflow,
            "total_available": total_available,
            "utilization_percent": round(
                ((checked_out / total_available) * 100) if total_available > 0 else 0,
                2
            )
        }
    except Exception as e:
        health_status["database"] = "disconnected"
        health_status["status"] = "degraded"
        health_status["database_error"] = str(e)
        
        # Add specific error type detection for better diagnostics
        error_str = str(e)
        if "Name or service not known" in error_str or "[Errno -2]" in error_str:
            health_status["error_type"] = "dns_resolution_failure"
            health_status["error_message"] = (
                "Database hostname cannot be resolved. "
                "Check DATABASE_URL in Railway Backend → Variables. "
                "Ensure it's a direct URL, not a variable reference (${{ }})."
            )
        elif "127.0.0.1" in error_str or "localhost:5433" in error_str:
            health_status["error_type"] = "localhost_connection"
            health_status["error_message"] = (
                "Backend is trying to connect to localhost. "
                "DATABASE_URL is not set. Connect PostgreSQL service to Backend in Railway."
            )
        elif "Connection refused" in error_str:
            health_status["error_type"] = "connection_refused"
            health_status["error_message"] = (
                "Database connection refused. PostgreSQL may not be running or accessible."
            )
        
        logger.warning(f"Database health check failed: {e}")
    
    # Check circuit breaker status
    try:
        from app.middleware.circuit_breaker import circuit_breaker
        health_status["circuit_breaker"] = {
            "state": circuit_breaker.state.value,
            "failure_count": circuit_breaker.failure_count,
            "failure_threshold": circuit_breaker.failure_threshold,
        }
    except Exception:
        health_status["circuit_breaker"] = {"state": "unknown"}
    
    return health_status


@app.get("/health", response_class=HTMLResponse)
@app.get("/health.json")
async def health_check(request: Request):
    """Health check endpoint - returns HTML dashboard or JSON based on Accept header."""
    health_status = await get_health_data()
    
    # Check if JSON is requested
    accept_header = request.headers.get("Accept", "")
    if "application/json" in accept_header or request.url.path.endswith(".json"):
        return JSONResponse(content=health_status)
    
    # Return HTML dashboard
    return HTMLResponse(content=generate_health_dashboard(health_status))


def generate_health_dashboard(health_data: dict) -> str:
    """Generate HTML dashboard for health status."""
    status = health_data.get("status", "unknown")
    database_status = health_data.get("database", "unknown")
    environment = health_data.get("environment", "unknown")
    timestamp = health_data.get("timestamp", "")
    
    # Determine urgency and impact
    if database_status == "connected" and status == "healthy":
        urgency_level = "low"
        urgency_color = "#10b981"  # green
        urgency_label = "All Systems Operational"
        impact = "None - System fully operational"
        stability = "100%"
    elif database_status == "disconnected":
        urgency_level = "critical"
        urgency_color = "#ef4444"  # red
        urgency_label = "Critical - Database Disconnected"
        impact = "High - All database operations failing, login and data management unavailable"
        stability = "0%"
    elif status == "degraded":
        urgency_level = "high"
        urgency_color = "#f59e0b"  # amber
        urgency_label = "Degraded - Service Issues"
        impact = "Medium - Some features may be unavailable"
        stability = "50%"
    else:
        urgency_level = "medium"
        urgency_color = "#f59e0b"
        urgency_label = "Unknown Status"
        impact = "Unknown - Unable to determine system state"
        stability = "Unknown"
    
    # Get pool metrics
    pool_data = health_data.get("database_pool", {})
    pool_size = pool_data.get("size", 0)
    checked_in = pool_data.get("checked_in", 0)
    checked_out = pool_data.get("checked_out", 0)
    overflow = pool_data.get("overflow", 0)
    max_overflow = pool_data.get("max_overflow", 0)
    total_available = pool_data.get("total_available", pool_size + max_overflow)
    utilization_percent = pool_data.get("utilization_percent", 0)
    
    # Circuit breaker data
    cb_data = health_data.get("circuit_breaker", {})
    cb_state = cb_data.get("state", "unknown")
    cb_failures = cb_data.get("failure_count", 0)
    cb_threshold = cb_data.get("failure_threshold", 5)
    
    # Error information
    error_type = health_data.get("error_type", "")
    error_message = health_data.get("error_message", "")
    database_error = health_data.get("database_error", "")
    
    # Determine chart color based on utilization
    chart_color = "#10b981"  # green
    if utilization_percent > 80:
        chart_color = "#ef4444"  # red
    elif utilization_percent > 50:
        chart_color = "#f59e0b"  # amber
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>System Health Dashboard - Lead Scoring System</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: #1f2937;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
        }}
        
        .header {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .header h1 {{
            font-size: 28px;
            margin-bottom: 8px;
            color: #111827;
        }}
        
        .header .subtitle {{
            color: #6b7280;
            font-size: 14px;
        }}
        
        .status-badge {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 14px;
            margin-top: 12px;
            background: {urgency_color};
            color: white;
        }}
        
        .grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        
        .card {{
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}
        
        .card h2 {{
            font-size: 18px;
            margin-bottom: 16px;
            color: #111827;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 0;
            border-bottom: 1px solid #e5e7eb;
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #6b7280;
            font-size: 14px;
        }}
        
        .metric-value {{
            font-weight: 600;
            font-size: 18px;
            color: #111827;
        }}
        
        .metric-value.high {{
            color: #ef4444;
        }}
        
        .metric-value.medium {{
            color: #f59e0b;
        }}
        
        .metric-value.low {{
            color: #10b981;
        }}
        
        .progress-bar {{
            width: 100%;
            height: 24px;
            background: #e5e7eb;
            border-radius: 12px;
            overflow: hidden;
            margin-top: 8px;
        }}
        
        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #10b981, #059669);
            transition: width 0.3s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-size: 12px;
            font-weight: 600;
        }}
        
        .progress-fill.medium {{
            background: linear-gradient(90deg, #f59e0b, #d97706);
        }}
        
        .progress-fill.high {{
            background: linear-gradient(90deg, #ef4444, #dc2626);
        }}
        
        .chart-container {{
            position: relative;
            height: 300px;
            margin-top: 16px;
        }}
        
        .alert {{
            background: #fef3c7;
            border-left: 4px solid #f59e0b;
            padding: 16px;
            border-radius: 8px;
            margin-top: 16px;
        }}
        
        .alert.critical {{
            background: #fee2e2;
            border-left-color: #ef4444;
        }}
        
        .alert h3 {{
            color: #92400e;
            margin-bottom: 8px;
            font-size: 16px;
        }}
        
        .alert.critical h3 {{
            color: #991b1b;
        }}
        
        .alert p {{
            color: #78350f;
            font-size: 14px;
            line-height: 1.6;
        }}
        
        .alert.critical p {{
            color: #7f1d1d;
        }}
        
        .refresh-indicator {{
            text-align: center;
            color: #6b7280;
            font-size: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid #e5e7eb;
        }}
        
        .timestamp {{
            color: #9ca3af;
            font-size: 12px;
            margin-top: 8px;
        }}
        
        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏥 System Health Dashboard</h1>
            <div class="subtitle">Lead Scoring System v2.0 - Real-time Monitoring</div>
            <div class="status-badge">{urgency_label}</div>
            <div class="timestamp">Last Updated: <span id="timestamp">{timestamp}</span></div>
        </div>
        
        <div class="grid">
            <div class="card">
                <h2>📊 System Status</h2>
                <div class="metric">
                    <span class="metric-label">Overall Status</span>
                    <span class="metric-value {urgency_level}">{status.upper()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Environment</span>
                    <span class="metric-value">{environment}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Urgency Level</span>
                    <span class="metric-value {urgency_level}">{urgency_level.upper()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">System Stability</span>
                    <span class="metric-value {urgency_level}">{stability}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🗄️ Database Status</h2>
                <div class="metric">
                    <span class="metric-label">Connection</span>
                    <span class="metric-value {('low' if database_status == 'connected' else 'critical')}">{database_status.upper()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Pool Size</span>
                    <span class="metric-value">{pool_size}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Active Connections</span>
                    <span class="metric-value {('high' if checked_out > total_available * 0.8 else 'low')}">{checked_out}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Available Connections</span>
                    <span class="metric-value">{total_available}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>⚡ Connection Pool</h2>
                <div class="metric">
                    <span class="metric-label">Utilization</span>
                    <span class="metric-value {('high' if utilization_percent > 80 else 'medium' if utilization_percent > 50 else 'low')}">{utilization_percent}%</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {('high' if utilization_percent > 80 else 'medium' if utilization_percent > 50 else 'low')}" style="width: {min(utilization_percent, 100)}%">
                        {utilization_percent}%
                    </div>
                </div>
                <div class="metric">
                    <span class="metric-label">Checked In</span>
                    <span class="metric-value">{checked_in}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Checked Out</span>
                    <span class="metric-value">{checked_out}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Overflow</span>
                    <span class="metric-value">{overflow} / {max_overflow}</span>
                </div>
            </div>
            
            <div class="card">
                <h2>🔌 Circuit Breaker</h2>
                <div class="metric">
                    <span class="metric-label">State</span>
                    <span class="metric-value {('high' if cb_state == 'open' else 'low')}">{cb_state.upper()}</span>
                </div>
                <div class="metric">
                    <span class="metric-label">Failures</span>
                    <span class="metric-value {('high' if cb_failures >= cb_threshold * 0.8 else 'medium' if cb_failures > 0 else 'low')}">{cb_failures} / {cb_threshold}</span>
                </div>
                <div class="progress-bar">
                    <div class="progress-fill {('high' if cb_failures >= cb_threshold * 0.8 else 'medium' if cb_failures > 0 else 'low')}" style="width: {min((cb_failures / cb_threshold) * 100, 100)}%">
                        {cb_failures} / {cb_threshold}
                    </div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>📈 Connection Pool Utilization</h2>
            <div class="chart-container">
                <canvas id="poolChart"></canvas>
            </div>
        </div>
        
        <div class="card">
            <h2>🎯 Impact Analysis</h2>
            <div class="metric">
                <span class="metric-label">Impact on System</span>
                <span class="metric-value {urgency_level}">{impact}</span>
            </div>
            <div class="metric">
                <span class="metric-label">Stability Score</span>
                <span class="metric-value {urgency_level}">{stability}</span>
            </div>
        </div>
        
        {f'''
        <div class="alert {"critical" if urgency_level == "critical" else ""}">
            <h3>⚠️ {'Critical Issue Detected' if urgency_level == 'critical' else 'Service Degradation'}</h3>
            <p><strong>Error Type:</strong> {error_type or 'Unknown'}</p>
            <p><strong>Message:</strong> {error_message or database_error or 'No additional error information available'}</p>
            <p><strong>Impact:</strong> {impact}</p>
        </div>
        ''' if database_status == 'disconnected' or status == 'degraded' else ''}
        
        <div class="refresh-indicator">
            <span id="refreshStatus">Auto-refreshing every 5 seconds...</span>
        </div>
    </div>
    
    <script>
        // Connection Pool Chart
        const poolCtx = document.getElementById('poolChart').getContext('2d');
        const poolChart = new Chart(poolCtx, {{
            type: 'doughnut',
            data: {{
                labels: ['Used Connections', 'Available Connections'],
                datasets: [{{
                    data: [{checked_out}, {total_available - checked_out}],
                    backgroundColor: [
                        '{chart_color}',
                        '#e5e7eb'
                    ],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                return context.label + ': ' + context.parsed + ' connections';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Auto-refresh every 5 seconds
        let refreshCount = 0;
        setInterval(() => {{
            refreshCount++;
            document.getElementById('refreshStatus').textContent = `Auto-refreshing every 5 seconds... (Refreshed ${{refreshCount}} times)`;
            location.reload();
        }}, 5000);
        
        // Update timestamp
        document.getElementById('timestamp').textContent = new Date().toLocaleString();
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
