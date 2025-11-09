"""Public API v1 router."""

from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from . import leads, users

router = APIRouter()
router.include_router(leads.router, prefix="/leads", tags=["public:leads"])
router.include_router(users.router, prefix="/users", tags=["public:users"])

_public_app = FastAPI(title="Lead Scoring Public API", version="1.0.0", docs_url=None, redoc_url=None)
_public_app.include_router(router)
_public_openapi_schema = get_openapi(
    title=_public_app.title,
    version=_public_app.version,
    routes=_public_app.routes,
)

docs_router = APIRouter()


@docs_router.get("/docs")
def public_api_docs():
    return get_swagger_ui_html(
        openapi_url="/api/v1/openapi.json",
        title="Lead Scoring Public API",
    )


@docs_router.get("/openapi.json")
def public_api_openapi():
    return JSONResponse(_public_openapi_schema)

