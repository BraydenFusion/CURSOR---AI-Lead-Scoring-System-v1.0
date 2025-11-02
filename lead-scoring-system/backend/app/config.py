"""Application configuration management using Pydantic settings."""

import os
import json
from functools import lru_cache
from pathlib import Path
from typing import Optional, List

from pydantic import Field
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, RedisDsn


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application settings pulled from environment variables."""

    app_name: str = Field("Lead Scoring System")
    environment: str = Field(default="development")

    # Database - Railway provides DATABASE_URL automatically
    # Handle both postgres:// (Railway) and postgresql:// formats
    database_url_str: str = Field(
        default="",
        description="Database URL from environment (Railway compatible).",
    )

    @property
    def database_url(self) -> str:
        """Get database URL, handling Railway's postgres:// format."""
        url = os.getenv("DATABASE_URL", self.database_url_str)
        if not url:
            url = "postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring"
        
        # Railway provides postgres:// but SQLAlchemy needs postgresql://
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
        elif url.startswith("postgresql://"):
            # Ensure we use psycopg driver
            if "+psycopg" not in url:
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        
        return url

    redis_url: RedisDsn = Field(
        default="redis://localhost:6379/0",
        description="Redis connection string for caching and task queueing.",
    )

    cors_origins_str: str = Field(
        default="http://localhost:5173",
        description="Comma-separated list of allowed CORS origins.",
    )

    @property
    def cors_origins(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from environment (Railway compatible)."""
        origins_str = os.getenv("ALLOWED_ORIGINS", self.cors_origins_str)
        if not origins_str:
            return ["http://localhost:5173"]
        
        # Handle both comma-separated string and JSON array
        if origins_str.startswith("["):
            try:
                return json.loads(origins_str)
            except json.JSONDecodeError:
                pass
        
        # Split comma-separated values
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]

    # Security
    secret_key: str = Field(
        default="",
        description="Secret key for JWT token signing. MUST be set in production!",
    )
    access_token_expire_minutes: int = Field(
        default=60 * 24,  # 24 hours
        description="JWT access token expiration time in minutes.",
    )

    # Email/SMTP Configuration (Optional)
    smtp_host: str = Field(default="smtp.gmail.com", description="SMTP server hostname.")
    smtp_port: int = Field(default=587, description="SMTP server port.")
    smtp_user: str = Field(default="", description="SMTP username/email.")
    smtp_password: str = Field(default="", description="SMTP password or app password.")
    from_email: str = Field(
        default="noreply@leadscoring.com",
        description="Default sender email address.",
    )

    # Railway-specific
    railway_environment: Optional[str] = Field(
        default=None, description="Railway environment name."
    )
    railway_project_id: Optional[str] = Field(
        default=None, description="Railway project ID."
    )
    port: int = Field(default=8000, description="Server port (Railway sets $PORT).")

    class Config:
        env_file = BASE_DIR.parent / ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Get Railway environment variables
        self.railway_environment = os.getenv("RAILWAY_ENVIRONMENT")
        self.railway_project_id = os.getenv("RAILWAY_PROJECT_ID")
        self.port = int(os.getenv("PORT", "8000"))


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached instance of application settings."""

    return Settings()  # type: ignore[call-arg]


def get_database_url(override: Optional[str] = None) -> str:
    """Helper to retrieve the database URL, allowing runtime overrides."""

    if override:
        return override

    settings = get_settings()
    return settings.database_url
