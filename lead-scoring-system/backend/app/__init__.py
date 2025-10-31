"""Backend application package for the lead scoring system."""

from fastapi import FastAPI


def create_app() -> FastAPI:
    """Factory helper for initializing the FastAPI application."""

    from .main import app  # local import to avoid circular dependencies

    return app
