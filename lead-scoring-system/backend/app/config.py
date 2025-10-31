"""Application configuration management using Pydantic settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import BaseSettings, Field, RedisDsn


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings pulled from environment variables."""

    app_name: str = Field("Lead Scoring System")
    environment: str = Field("development")

    database_url: str = Field(
        "postgresql+psycopg://postgres:postgres@localhost:5432/lead_scoring",
        description="SQLAlchemy-compatible PostgreSQL DSN.",
    )
    redis_url: RedisDsn = Field(
        "redis://localhost:6379/0",
        description="Redis connection string for caching and task queueing.",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "*"])

    class Config:
        env_file = BASE_DIR.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of application settings."""

    return Settings()  # type: ignore[call-arg]


def get_database_url(override: Optional[str] = None) -> str:
    """Helper to retrieve the database URL, allowing runtime overrides."""

    if override:
        return override

    return str(get_settings().database_url)
