"""Route aggregates for the API."""

from .leads import router as leads_router
from .activities import router as activities_router
from .scoring import router as scoring_router
from .auth import router as auth_router
from .assignments import router as assignments_router
from .notes import router as notes_router
from .notifications import router as notifications_router
from .upload import router as upload_router
from .dashboard import router as dashboard_router
from .profile import router as profile_router
from .analytics import router as analytics_router
from .reports import router as reports_router

# Import debug router if it exists
try:
    from .debug import router as debug_router
except ImportError:
    debug_router = None

__all__ = [
    "leads_router",
    "activities_router",
    "scoring_router",
    "auth_router",
    "assignments_router",
    "notes_router",
    "notifications_router",
    "upload_router",
    "dashboard_router",
    "profile_router",
    "analytics_router",
    "reports_router",
]

if debug_router:
    __all__.append("debug_router")
