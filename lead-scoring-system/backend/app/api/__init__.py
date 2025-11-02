"""API package exposing the root router."""

from fastapi import APIRouter

from .routes import (
    activities_router,
    assignments_router,
    auth_router,
    leads_router,
    notes_router,
    notifications_router,
    scoring_router,
)


router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(leads_router, prefix="/leads", tags=["leads"])
router.include_router(activities_router, prefix="/leads", tags=["activities"])
router.include_router(scoring_router, prefix="/leads", tags=["scoring"])
router.include_router(assignments_router, prefix="/assignments", tags=["assignments"])
router.include_router(notes_router, prefix="/notes", tags=["notes"])
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
