"""Circuit breaker middleware for database operations to prevent cascade failures."""

import logging
import time
from enum import Enum
from typing import Optional
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from fastapi import status
from sqlalchemy.exc import SQLAlchemyError, OperationalError

logger = logging.getLogger(__name__)


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class DatabaseCircuitBreaker:
    """Circuit breaker pattern for database operations."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        self.failure_count = 0
        self.success_count = 0
        self.state = CircuitState.CLOSED
        self.last_failure_time: Optional[float] = None
        
    def record_success(self):
        """Record a successful operation."""
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                logger.info("✅ Circuit breaker: Database recovered, closing circuit")
                self.state = CircuitState.CLOSED
                self.failure_count = 0
                self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            # Reset failure count on success
            if self.failure_count > 0:
                self.failure_count = max(0, self.failure_count - 1)
    
    def record_failure(self):
        """Record a failed operation."""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.state == CircuitState.HALF_OPEN:
            # Failed again during recovery, open circuit
            logger.error("❌ Circuit breaker: Database still failing, opening circuit")
            self.state = CircuitState.OPEN
            self.success_count = 0
        elif self.state == CircuitState.CLOSED:
            if self.failure_count >= self.failure_threshold:
                logger.error(f"❌ Circuit breaker: Opening circuit after {self.failure_count} failures")
                self.state = CircuitState.OPEN
    
    def should_allow(self) -> bool:
        """Check if operation should be allowed."""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                time_since_failure = time.time() - self.last_failure_time
                if time_since_failure >= self.recovery_timeout:
                    logger.info("🔄 Circuit breaker: Entering half-open state, testing recovery")
                    self.state = CircuitState.HALF_OPEN
                    self.success_count = 0
                    return True
            return False
        
        return True  # CLOSED or HALF_OPEN states allow operations


# Global circuit breaker instance
circuit_breaker = DatabaseCircuitBreaker()


class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    """Middleware to implement circuit breaker for database operations."""
    
    async def dispatch(self, request: Request, call_next):
        # Only apply to routes that use database
        if not any(path in request.url.path for path in ["/api/", "/auth/", "/health"]):
            return await call_next(request)
        
        # Check circuit breaker before processing
        if not circuit_breaker.should_allow():
            logger.warning(f"Circuit breaker OPEN: Rejecting request to {request.url.path}")
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content={
                    "detail": "Database service temporarily unavailable. Please try again in a moment.",
                    "type": "circuit_breaker_open",
                },
            )
        
        try:
            response = await call_next(request)
            
            # Record success for successful responses
            if response.status_code < 500:
                circuit_breaker.record_success()
            else:
                # Only count database-related 500s as failures
                if "database" in response.body.decode(errors="ignore").lower() if hasattr(response, 'body') else False:
                    circuit_breaker.record_failure()
            
            return response
            
        except (SQLAlchemyError, OperationalError) as e:
            # Database errors trigger circuit breaker
            circuit_breaker.record_failure()
            logger.error(f"Database error triggering circuit breaker: {e}")
            raise  # Let error handler deal with it
        except Exception:
            # Re-raise to let error handlers deal with it
            raise

