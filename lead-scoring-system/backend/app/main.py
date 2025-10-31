"""FastAPI application entry point for the lead scoring backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router
from .config import get_settings


settings = get_settings()

app = FastAPI(title="Lead Scoring System", version="1.0.0")


def configure_cors(application: FastAPI) -> None:
    """Configure CORS settings for the API."""

    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routers(application: FastAPI) -> None:
    """Attach API routers to the application instance."""

    application.include_router(api_router, prefix="/api")


@app.get("/", tags=["health"])
def root() -> dict[str, str]:
    """Simple root endpoint for connectivity checks."""

    return {"message": "Lead Scoring API v1.0"}


@app.get("/health", tags=["health"])
def health_check() -> dict[str, str]:
    """Basic health check endpoint."""

    return {"status": "healthy"}


configure_cors(app)
configure_routers(app)
