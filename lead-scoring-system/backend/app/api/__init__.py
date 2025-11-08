"""API package exposing the root router."""

from fastapi import APIRouter

from .routes import (
    activities_router,
    assignments_router,
    assignment_rules_router,
    auth_router,
    analytics_router,
    reports_router,
    dashboard_router,
    leads_router,
    notes_router,
    notifications_router,
    profile_router,
    scoring_router,
    upload_router,
    ai_router,
)

# Import debug router if it exists
try:
    from .routes import debug_router
except ImportError:
    debug_router = None


router = APIRouter()

router.include_router(auth_router, prefix="/auth", tags=["authentication"])
router.include_router(profile_router, prefix="/auth", tags=["profile"])
router.include_router(leads_router, prefix="/leads", tags=["leads"])
router.include_router(activities_router, prefix="/leads", tags=["activities"])
router.include_router(scoring_router, prefix="/leads", tags=["scoring"])
router.include_router(upload_router, prefix="/upload", tags=["upload"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
router.include_router(assignments_router, prefix="/assignments", tags=["assignments"])
router.include_router(assignment_rules_router, prefix="/assignment-rules", tags=["assignment_rules"])
router.include_router(notes_router, prefix="/notes", tags=["notes"])
router.include_router(notifications_router, prefix="/notifications", tags=["notifications"])
router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])
router.include_router(reports_router, prefix="/reports", tags=["reports"])
router.include_router(ai_router, prefix="/ai", tags=["ai"])

# Include debug router if available
if debug_router:
    router.include_router(debug_router, prefix="/debug", tags=["debug"])
