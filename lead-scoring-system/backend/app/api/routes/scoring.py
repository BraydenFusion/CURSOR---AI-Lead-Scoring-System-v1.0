"""Scoring endpoints for leads."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas import ScoreResponse


router = APIRouter()


@router.get("/{lead_id}/score", response_model=ScoreResponse)
def get_lead_score(lead_id: UUID, db: Session = Depends(get_db)) -> ScoreResponse:
    """Return the calculated score for a lead."""

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
