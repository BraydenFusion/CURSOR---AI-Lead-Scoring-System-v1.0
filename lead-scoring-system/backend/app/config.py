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
    
    # OpenAI API Key for AI-powered lead scoring
    openai_api_key: str = Field(default="", validation_alias="OPENAI_API_KEY")
    
    # Google OAuth for Google Sign-In / Email integration
    google_client_id: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_ID")
    google_client_secret: Optional[str] = Field(default=None, validation_alias="GOOGLE_CLIENT_SECRET")
    google_oauth_redirect_uri: Optional[str] = Field(default=None, validation_alias="GOOGLE_OAUTH_REDIRECT_URI")

    # Outlook OAuth (Microsoft Graph)
    outlook_client_id: Optional[str] = Field(default=None, validation_alias="OUTLOOK_CLIENT_ID")
    outlook_client_secret: Optional[str] = Field(default=None, validation_alias="OUTLOOK_CLIENT_SECRET")
    outlook_oauth_redirect_uri: Optional[str] = Field(default=None, validation_alias="OUTLOOK_OAUTH_REDIRECT_URI")

    # Encryption key for storing third-party tokens securely (Fernet base64 key)
    email_encryption_key: str = Field(default="", validation_alias="EMAIL_ENCRYPTION_KEY")

    # CRM defaults and tuning
    pipedrive_base_url: str = Field(default="https://api.pipedrive.com/v1", validation_alias="PIPEDRIVE_BASE_URL")
    crm_sync_interval_seconds: int = Field(default=3600, validation_alias="CRM_SYNC_INTERVAL_SECONDS")
    crm_sync_max_retries: int = Field(default=3, validation_alias="CRM_SYNC_MAX_RETRIES")

    # Database - Railway provides DATABASE_URL automatically
    # Handle both postgres:// (Railway) and postgresql:// formats
    database_url_str: str = Field(
        default="",
        description="Database URL from environment (Railway compatible).",
        validation_alias="DATABASE_URL",  # Pydantic alias to read from DATABASE_URL env var
    )

    @property
    def database_url(self) -> str:
        """Get database URL, handling Railway's postgres:// format."""
        import logging
        logger = logging.getLogger(__name__)
        
        # Debug: Check all possible sources
        logger.info("=" * 60)
        logger.info("🔍 DATABASE_URL Debug Information:")
        logger.info(f"   os.getenv('DATABASE_URL'): {bool(os.getenv('DATABASE_URL'))}")
        logger.info(f"   self.database_url_str: {bool(self.database_url_str)}")
        logger.info(f"   Type of database_url_str: {type(self.database_url_str)}")
        
        # Try multiple sources (Railway might use different env var names)
        url = (
            os.getenv("DATABASE_URL") or
            os.getenv("POSTGRES_URL") or
            os.getenv("PGDATABASE") or
            os.getenv("POSTGRES_DATABASE_URL") or
            (self.database_url_str if self.database_url_str else None)
        )
        
        if url:
            logger.info(f"   Found URL from: {self._get_url_source(url)}")
            logger.info(f"   URL length: {len(url)}")
            logger.info(f"   URL starts with: {url[:20]}..." if len(url) > 20 else f"   URL: {url}")
        else:
            logger.warning("   No URL found in any source!")
        
        logger.info("=" * 60)
        
        # Check if it's a Railway variable reference (not resolved)
        if url and url.startswith("${{"):
            logger.error(f"⚠️  DATABASE_URL appears to be an unresolved Railway reference: {url}")
            logger.error("⚠️  This means the variable reference is not resolving!")
            logger.error("⚠️  Railway variable references sometimes don't work.")
            logger.error("⚠️  SOLUTION: Manually copy the DATABASE_URL value from PostgreSQL service → Variables")
            # Fall back to default
            url = None
        
        if not url or url.strip() == "":
            url = "postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring"
            logger.warning(f"⚠️  No DATABASE_URL found, using default: {url}")
            logger.warning("⚠️  TO FIX: Set DATABASE_URL in Railway Backend Service → Variables")
            logger.warning("⚠️  Copy the value from PostgreSQL Service → Variables → DATABASE_URL")
        else:
            logger.info(f"✅ DATABASE_URL found (length: {len(url)})")
        
        # Railway provides postgres:// but SQLAlchemy needs postgresql://
        original_url = url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)
            logger.info("   Converted postgres:// to postgresql+psycopg://")
        elif url.startswith("postgresql://"):
            # Ensure we use psycopg driver
            if "+psycopg" not in url:
                url = url.replace("postgresql://", "postgresql+psycopg://", 1)
                logger.info("   Added psycopg driver to postgresql://")
        
        if original_url != url:
            logger.info(f"   Final URL format: {url[:30]}..." if len(url) > 30 else f"   Final URL: {url}")
        
        return url
    
    def _get_url_source(self, url: str) -> str:
        """Determine which source provided the URL."""
        if os.getenv("DATABASE_URL") == url:
            return "DATABASE_URL env var"
        elif os.getenv("POSTGRES_URL") == url:
            return "POSTGRES_URL env var"
        elif os.getenv("PGDATABASE") == url:
            return "PGDATABASE env var"
        elif os.getenv("POSTGRES_DATABASE_URL") == url:
            return "POSTGRES_DATABASE_URL env var"
        elif self.database_url_str == url:
            return "database_url_str field"
        else:
            return "unknown source"

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
    public_api_default_rate_limit: int = Field(
        default=100,
        description="Default requests per hour for public API keys.",
    )

    # Email/SMTP Configuration (Optional)
    smtp_host: str = Field(
        default="smtp.gmail.com",
        description="SMTP server hostname.",
        validation_alias="SMTP_HOST",
    )
    smtp_port: int = Field(
        default=587,
        description="SMTP server port.",
        validation_alias="SMTP_PORT",
    )
    smtp_user: str = Field(
        default="",
        description="SMTP username/email.",
        validation_alias="SMTP_USERNAME",
    )
    smtp_password: str = Field(
        default="",
        description="SMTP password or app password.",
        validation_alias="SMTP_PASSWORD",
    )
    from_email: str = Field(
        default="noreply@leadscoring.com",
        description="Default sender email address.",
        validation_alias="SMTP_FROM_EMAIL",
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
