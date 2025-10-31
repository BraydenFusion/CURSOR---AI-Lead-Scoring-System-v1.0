"""Scoring endpoints for leads."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas import ScoreResponse
from ...services.scoring_service import ScoringService


router = APIRouter()


@router.get("/{lead_id}/score", response_model=ScoreResponse)
def get_lead_score(lead_id: UUID, db: Session = Depends(get_db)) -> ScoreResponse:
    """Return the calculated score for a lead."""

    try:
        result = ScoringService.calculate_lead_score(db, lead_id)
        return ScoreResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
