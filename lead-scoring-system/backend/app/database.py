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

logger.info(f"Connecting to database (Railway: {settings.railway_environment or 'local'})")

# Create engine with Railway-optimized settings
engine = create_engine(
    DATABASE_URL,
    echo=False,
    future=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=10,        # Railway handles this well
    max_overflow=20
)

SessionLocal = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
)

Base = declarative_base()


def get_db() -> Generator:
    """Provide a transactional scope around a series of operations."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
