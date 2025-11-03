"""Database configuration and session management."""

import logging
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

from .config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Use the property that handles postgres:// to postgresql:// conversion
DATABASE_URL = settings.database_url

# Log database URL (masked for security)
def mask_url(url: str) -> str:
    """Mask sensitive parts of database URL for logging."""
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

logger.info(f"Connecting to database (Railway: {settings.railway_environment or 'local'})")
logger.info(f"Database URL: {mask_url(DATABASE_URL)}")

# Check if using default localhost URL (indicates DATABASE_URL not set)
if "localhost:5433" in DATABASE_URL or "127.0.0.1:5433" in DATABASE_URL:
    logger.warning("⚠️  Using default localhost database URL - DATABASE_URL environment variable may not be set!")
    logger.warning("⚠️  Please ensure PostgreSQL service is connected to backend service in Railway")

# Create engine with Railway-optimized settings for high capacity
# Increased pool sizes for better load handling
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,        # Verify connections before using (prevents stale connections)
    pool_recycle=3600,         # Recycle connections after 1 hour (prevents timeout errors)
    pool_size=20,              # Increased base pool size for higher capacity (was 10)
    max_overflow=40,           # Increased overflow for burst traffic (was 20)
    pool_timeout=30,           # Timeout waiting for connection from pool (seconds)
    connect_args={
        "connect_timeout": 10,  # Connection timeout (seconds)
        # TCP keepalive settings for psycopg3
        # These help maintain stable connections in cloud environments
    },
    # Add query timeout to prevent long-running queries from blocking
    execution_options={
        "autocommit": False,
        "isolation_level": "READ COMMITTED",  # Lower isolation for better concurrency
    }
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
)

Base = declarative_base()


def get_db() -> Generator:
    """Provide a transactional scope around a series of operations with error recovery."""
    db = SessionLocal()
    try:
        yield db
        # Note: FastAPI dependency system handles commit/rollback via Depends()
        # Explicit commits should only be done in routes that need it
    except Exception as e:
        db.rollback()  # Rollback on any error
        logger.error(f"Database transaction error: {e}")
        raise
    finally:
        db.close()
