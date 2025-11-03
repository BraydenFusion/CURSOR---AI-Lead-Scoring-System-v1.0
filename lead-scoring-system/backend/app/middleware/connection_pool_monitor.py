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
                try:
                    checked_out = pool.checkedout()
                    checked_in = pool.checkedin()
                    total_connections = checked_out + checked_in
                    pool_size = pool.size()
                    max_overflow = getattr(pool, "_max_overflow", 0) or getattr(pool, "_overflow", 0) or 0
                    max_connections = pool_size + max_overflow
                    
                    if max_connections > 0 and total_connections > max_connections * 0.8:
                        logger.warning(
                            f"⚠️  Connection pool usage high: "
                            f"{checked_out} checked out, {checked_in} checked in "
                            f"({total_connections}/{max_connections} total)"
                        )
                except Exception as e:
                    # Pool might not expose these attributes, ignore
                    logger.debug(f"Could not read pool stats: {e}")
        except Exception as e:
            # Don't fail requests if monitoring fails
            logger.debug(f"Pool monitoring error (non-critical): {e}")
        
        response = await call_next(request)
        return response

