"""Lead activity endpoints."""

from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Lead, LeadActivity
from ...schemas import ActivityCreate, ActivityRead
from ...services.scoring_service import ScoringService


router = APIRouter()


@router.post("/{lead_id}/activity", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
def log_activity(lead_id: UUID, payload: ActivityCreate, db: Session = Depends(get_db)) -> LeadActivity:
    """Record a new activity for the given lead and refresh their score."""

    lead_exists = db.query(Lead.id).filter(Lead.id == lead_id).first()
    if lead_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    if payload.lead_id and payload.lead_id != lead_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="lead_id mismatch between path and payload")

    timestamp = payload.timestamp or datetime.utcnow()
    points_awarded = ScoringService.activity_base_points(payload.activity_type)

    activity = LeadActivity(
        lead_id=lead_id,
        activity_type=payload.activity_type,
        timestamp=timestamp,
        metadata=payload.metadata or {},
        points_awarded=points_awarded,
    )

    try:
        db.add(activity)
        db.commit()
        db.refresh(activity)
    except Exception as exc:  # pragma: no cover - defensive safeguard
        db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    ScoringService.update_lead_score(db, lead_id, activity.id)
    db.refresh(activity)

    return activity


@router.get("/{lead_id}/activities", response_model=List[ActivityRead])
def list_activities(lead_id: UUID, db: Session = Depends(get_db)) -> List[LeadActivity]:
    """List activities for a given lead."""

    lead_exists = db.query(Lead.id).filter(Lead.id == lead_id).first()
    if lead_exists is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    activities = (
        db.query(LeadActivity)
        .filter(LeadActivity.lead_id == lead_id)
        .order_by(LeadActivity.timestamp.desc())
        .all()
    )

    return activities
