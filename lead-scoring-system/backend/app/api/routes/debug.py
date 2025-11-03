"""Debug endpoints for troubleshooting."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from app.config import get_settings

settings = get_settings()
router = APIRouter()


@router.get("/cors")
def debug_cors(request: Request):
    """Debug CORS configuration."""
    origin = request.headers.get("origin")
    
    return JSONResponse(
        content={
            "request_origin": origin,
            "cors_origins": settings.cors_origins,
            "environment": settings.railway_environment or settings.environment,
            "headers": {
                "origin": request.headers.get("origin"),
                "referer": request.headers.get("referer"),
            },
        },
        headers={
            "Access-Control-Allow-Origin": origin or "*",
            "Access-Control-Allow-Credentials": "true",
        }
    )

