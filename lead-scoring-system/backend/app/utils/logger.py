"""Structured logging configuration."""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

from app.config import get_settings

settings = get_settings()


def setup_logging(log_level: str | None = None):
    """Set up application logging with file rotation."""

    # Get log level from settings or use provided
    level = log_level or ("DEBUG" if settings.environment == "development" else "INFO")

    # Create logs directory if it doesn't exist
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(getattr(logging, level.upper()))

    # Clear existing handlers
    logger.handlers.clear()

    # Console handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)

    # File handler with rotation
    file_handler = RotatingFileHandler(
        logs_dir / "app.log", maxBytes=10485760, backupCount=5  # 10MB per file, keep 5 backups
    )
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(pathname)s:%(lineno)d - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    file_handler.setFormatter(file_formatter)

    # Error file handler (separate file for errors)
    error_handler = RotatingFileHandler(
        logs_dir / "error.log", maxBytes=10485760, backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_formatter)

    # Add handlers
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)

    # Set levels for third-party loggers
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)

    return logger

