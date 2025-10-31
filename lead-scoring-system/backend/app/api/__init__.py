"""API package exposing the root router."""

from fastapi import APIRouter

from .routes import leads_router, activities_router, scoring_router


router = APIRouter()

router.include_router(leads_router, prefix="/leads", tags=["leads"])
router.include_router(activities_router, prefix="/leads", tags=["activities"])
router.include_router(scoring_router, prefix="/leads", tags=["scoring"])
