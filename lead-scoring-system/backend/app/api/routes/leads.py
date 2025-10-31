"""Lead-related API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Lead
from ...schemas import LeadCreate, LeadListResponse, LeadRead


router = APIRouter()


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    """Create a new lead and persist it to the database."""

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("", response_model=LeadListResponse)
def list_leads(
    sort: str = "score",
    classification: str = "all",
    page: int = 1,
    per_page: int = 25,
    db: Session = Depends(get_db),
) -> LeadListResponse:
    """Return a paginated list of leads."""

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)) -> Lead:
    """Retrieve lead details by identifier."""

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
