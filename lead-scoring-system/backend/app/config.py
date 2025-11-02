"""Application configuration management using Pydantic settings."""

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings pulled from environment variables."""

    app_name: str = Field("Lead Scoring System")
    environment: str = Field("development")

    database_url: PostgresDsn = Field(
        "postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring",
        description="SQLAlchemy-compatible PostgreSQL DSN.",
    )
    redis_url: RedisDsn = Field(
        "redis://localhost:6379/0",
        description="Redis connection string for caching and task queueing.",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:5173", "*"])

    # Security
    secret_key: str = Field(
        default="DEV-ONLY-CHANGE-IN-PRODUCTION-use-long-random-string-here",
        description="Secret key for JWT token signing. MUST be changed in production!",
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24,  # 24 hours
        description="JWT access token expiration time in minutes.",
    )

    # Email/SMTP Configuration
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server hostname.")
    smtp_port: int = Field(default=587, description="SMTP server port.")
    smtp_user: str = Field(default="", description="SMTP username/email.")
    smtp_password: str = Field(default="", description="SMTP password or app password.")
    from_email: str = Field(
        default="noreply@leadscoring.com",
        description="Default sender email address.",
    )

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
