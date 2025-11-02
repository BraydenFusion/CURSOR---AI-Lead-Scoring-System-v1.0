"""Scoring endpoints for leads."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.lead import Lead
from ...schemas import ScoreResponse
from ...services.scoring_service import calculate_lead_score


router = APIRouter()


@router.get("/{lead_id}/score", response_model=ScoreResponse)
def get_lead_score(lead_id: UUID, db: Session = Depends(get_db)) -> ScoreResponse:
    """Return the calculated score for a lead."""

    try:
        # Check if lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with id {lead_id} not found"
            )

        # Calculate score (this will update the lead if needed)
        score_data = calculate_lead_score(lead_id, db)

        # Return score response
        return ScoreResponse(
            total_score=score_data["total_score"],
            classification=score_data["classification"],
            breakdown=score_data["breakdown"],
            details=score_data["details"],
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error calculating score: {str(e)}"
        )
