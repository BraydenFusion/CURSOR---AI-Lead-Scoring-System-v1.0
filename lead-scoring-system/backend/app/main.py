"""FastAPI application entry point for the lead scoring backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router as api_router


app = FastAPI(title="Lead Scoring System", version="1.0.0")


def configure_cors(application: FastAPI) -> None:
    """Configure permissive CORS for the MVP environment."""

    application.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


def configure_routers(application: FastAPI) -> None:
    """Attach API routers to the application instance."""

    application.include_router(api_router, prefix="/api")


configure_cors(app)
configure_routers(app)
