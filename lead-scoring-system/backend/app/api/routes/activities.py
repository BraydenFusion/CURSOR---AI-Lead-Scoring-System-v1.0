"""Lead activity endpoints."""

from typing import List
from uuid import UUID, uuid4
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.lead import Lead
from ...models.activity import LeadActivity
from ...schemas import ActivityCreate, ActivityRead
from ...services.scoring_service import calculate_lead_score


router = APIRouter()


@router.post("/{lead_id}/activity", response_model=ActivityRead, status_code=status.HTTP_201_CREATED)
def log_activity(lead_id: UUID, payload: ActivityCreate, db: Session = Depends(get_db)) -> ActivityRead:
    """Record a new activity for the given lead."""

    try:
        # Check if lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with id {lead_id} not found"
            )

        # Create activity
        activity = LeadActivity(
            id=uuid4(),
            lead_id=lead_id,
            activity_type=payload.activity_type,
            points_awarded=payload.points_awarded,
            timestamp=payload.timestamp or datetime.utcnow(),
            _metadata=payload.metadata,
        )

        db.add(activity)
        db.flush()

        # Recalculate lead score after activity is added
        calculate_lead_score(lead_id, db)

        # Refresh activity to get any updates
        db.refresh(activity)

        # Convert to dict format, mapping _metadata to metadata
        activity_dict = {
            "id": activity.id,
            "lead_id": activity.lead_id,
            "activity_type": activity.activity_type,
            "points_awarded": activity.points_awarded,
            "timestamp": activity.timestamp,
            "metadata": activity._metadata if hasattr(activity, '_metadata') else {},
        }
        return ActivityRead.model_validate(activity_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating activity: {str(e)}"
        )


@router.get("/{lead_id}/activities", response_model=List[ActivityRead])
def list_activities(lead_id: UUID, db: Session = Depends(get_db)) -> List[ActivityRead]:
    """List activities for a given lead."""

    try:
        # Check if lead exists
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with id {lead_id} not found"
            )

        # Get all activities for the lead, ordered by timestamp (most recent first)
        activities = (
            db.query(LeadActivity)
            .filter(LeadActivity.lead_id == lead_id)
            .order_by(LeadActivity.timestamp.desc())
            .all()
        )

        # Convert activities to dict format, mapping _metadata to metadata
        activity_dicts = []
        for activity in activities:
            activity_dict = {
                "id": activity.id,
                "lead_id": activity.lead_id,
                "activity_type": activity.activity_type,
                "points_awarded": activity.points_awarded,
                "timestamp": activity.timestamp,
                "metadata": activity._metadata if hasattr(activity, '_metadata') else {},
            }
            activity_dicts.append(activity_dict)
        
        return [ActivityRead.model_validate(ad) for ad in activity_dicts]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing activities: {str(e)}"
        )
