"""Lead activity endpoints."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...schemas import ActivityCreate, ActivityRead


router = APIRouter()


@router.post("/{lead_id}/activity", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
def log_activity(lead_id: UUID, payload: ActivityCreate, db: Session = Depends(get_db)) -> ActivityRead:
    """Record a new activity for the given lead."""

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)


@router.get("/{lead_id}/activities", response_model=List[ActivityRead])
def list_activities(lead_id: UUID, db: Session = Depends(get_db)) -> List[ActivityRead]:
    """List activities for a given lead."""

    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED)
