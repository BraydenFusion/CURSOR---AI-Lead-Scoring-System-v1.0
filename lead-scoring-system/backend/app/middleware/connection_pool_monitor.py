"""Middleware to monitor and log connection pool usage."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class ConnectionPoolMonitor(BaseHTTPMiddleware):
    """Monitor database connection pool usage and log warnings if pool is exhausted."""

    async def dispatch(self, request: Request, call_next):
        # Check pool status before request
        try:
            from app.database import engine
            pool = engine.pool
            
            # Log pool stats periodically (every 100 requests to avoid spam)
            import random
            if random.randint(1, 100) == 1:  # 1% chance to log
                logger.debug(
                    f"Connection pool: size={pool.size()}, "
                    f"checked_in={pool.checkedin()}, "
                    f"checked_out={pool.checkedout()}, "
                    f"overflow={pool.overflow()}, "
                    f"invalid={pool.invalid()}"
                )
                
                # Warn if pool is getting full
                total_connections = pool.checkedout() + pool.checkedin()
                max_connections = pool.size() + (pool._overflow or 0)
                
                if total_connections > max_connections * 0.8:
                    logger.warning(
                        f"⚠️  Connection pool usage high: "
                        f"{total_connections}/{max_connections} connections in use"
                    )
        except Exception as e:
            # Don't fail requests if monitoring fails
            logger.debug(f"Pool monitoring error (non-critical): {e}")
        
        response = await call_next(request)
        return response

