"""Database configuration and session management."""

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import get_database_url


DATABASE_URL = get_database_url()


engine = create_engine(DATABASE_URL, echo=False, future=True, pool_pre_ping=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)

Base = declarative_base()


def get_db() -> Generator:
    """Provide a transactional scope around a series of operations."""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
