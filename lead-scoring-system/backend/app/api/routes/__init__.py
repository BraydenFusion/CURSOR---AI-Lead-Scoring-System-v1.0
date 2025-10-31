"""Route aggregates for the API."""

from .leads import router as leads_router
from .activities import router as activities_router
from .scoring import router as scoring_router

__all__ = ["leads_router", "activities_router", "scoring_router"]
