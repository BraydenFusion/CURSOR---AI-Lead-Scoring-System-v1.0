"""Lead-related API routes."""

from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy import desc
from sqlalchemy.orm import Session, joinedload

from datetime import datetime

from ...database import get_db
from ...models.lead import Lead
from ...models.user import User
from ...schemas import LeadCreate, LeadListResponse, LeadRead, LeadStatusUpdate
from ...services.scoring_service import calculate_lead_score
from ...services import auto_assign_lead
from ...utils.auth import get_current_active_user


router = APIRouter()


@router.post("", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(
    payload: LeadCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LeadRead:
    """Create a new lead and persist it to the database."""

    try:
        # Check if email already exists
        existing_lead = db.query(Lead).filter(Lead.email == payload.email).first()
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Lead with email {payload.email} already exists"
            )

        # Create new lead with ownership
        lead = Lead(
            id=uuid4(),
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            source=payload.source,
            location=payload.location,
            created_by=current_user.id,
            _metadata=payload.metadata,
            current_score=0,
            classification=None,
        )

        db.add(lead)
        db.flush()  # Flush to get the ID

        # Calculate initial score using AI scoring (PRD)
        try:
            from ...services.ai_scoring import calculate_overall_score
            calculate_overall_score(lead.id, db)
        except Exception:
            # Fallback to legacy scoring if AI scoring fails
            calculate_lead_score(lead.id, db)

        # Refresh to get updated score
        db.refresh(lead)

        if payload.auto_assign:
            background_tasks.add_task(auto_assign_lead, lead.id)

        # Convert to dict format, mapping _metadata to metadata
        lead_dict = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
            "location": lead.location,
            "metadata": lead._metadata if hasattr(lead, '_metadata') else {},
            "current_score": lead.current_score,
            "classification": lead.classification,
            "status": lead.status,
            "contacted_at": lead.contacted_at,
            "qualified_at": lead.qualified_at,
            "closed_at": lead.closed_at,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
        }
        return LeadRead.model_validate(lead_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lead: {str(e)}"
        )


@router.get("", response_model=LeadListResponse)
def list_leads(
    sort: str = "score",
    classification: str = "all",
    page: int = 1,
    per_page: int = 25,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LeadListResponse:
    """Return a paginated list of leads.
    
    - Sales Reps: Only see their own leads
    - Managers: See all sales reps' leads
    - Owners/Admins: See all leads
    """

    try:
        # Base query with eager loading to avoid N+1 queries
        query = db.query(Lead).options(
            # Optionally load relationships if needed
            # joinedload(Lead.assignments),
            # joinedload(Lead.notes)
        )
        
        # Role-based filtering
        from app.models.user import UserRole
        user_role = current_user.get_role_enum()
        if user_role == UserRole.SALES_REP:
            # Sales reps only see their own leads
            query = query.filter(Lead.created_by == current_user.id)
        elif user_role == UserRole.MANAGER:
            # Managers see all leads (no filter)
            pass
        elif user_role == UserRole.ADMIN:
            # Admins/Owners see all leads (no filter)
            pass

        # Filter by classification
        if classification != "all":
            if classification not in ["hot", "warm", "cold"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Classification must be 'hot', 'warm', 'cold', or 'all'"
                )
            query = query.filter(Lead.classification == classification)

        # Sorting
        if sort == "score":
            query = query.order_by(desc(Lead.current_score))
        elif sort == "date":
            query = query.order_by(desc(Lead.created_at))
        elif sort == "name":
            query = query.order_by(Lead.name)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Sort must be 'score', 'date', or 'name'"
            )

        # Get total count before pagination
        total = query.count()

        # Pagination
        if page < 1:
            page = 1
        if per_page < 1:
            per_page = 25
        if per_page > 100:
            per_page = 100

        offset = (page - 1) * per_page
        leads = query.offset(offset).limit(per_page).all()

        # Convert leads to dict format for Pydantic, mapping _metadata to metadata
        lead_dicts = []
        for lead in leads:
            lead_dict = {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "phone": lead.phone,
                "source": lead.source,
                "location": lead.location,
                "metadata": lead._metadata if hasattr(lead, '_metadata') else {},
                "current_score": lead.current_score,
                "classification": lead.classification,
                "status": lead.status,
                "contacted_at": lead.contacted_at,
                "qualified_at": lead.qualified_at,
                "closed_at": lead.closed_at,
                "created_at": lead.created_at,
                "updated_at": lead.updated_at,
            }
            lead_dicts.append(lead_dict)
        
        return LeadListResponse(
            items=[LeadRead.model_validate(ld) for ld in lead_dicts],
            total=total,
            page=page,
            per_page=per_page,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing leads: {str(e)}"
        )


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)) -> LeadRead:
    """Retrieve lead details by identifier."""

    try:
        lead = db.query(Lead).filter(Lead.id == lead_id).first()
        if not lead:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Lead with id {lead_id} not found"
            )

        # Convert to dict format, mapping _metadata to metadata
        lead_dict = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
            "location": lead.location,
            "metadata": lead._metadata if hasattr(lead, '_metadata') else {},
            "current_score": lead.current_score,
            "classification": lead.classification,
            "status": lead.status,
            "contacted_at": lead.contacted_at,
            "qualified_at": lead.qualified_at,
            "closed_at": lead.closed_at,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
        }
        return LeadRead.model_validate(lead_dict)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving lead: {str(e)}"
        )


@router.put("/{lead_id}/status", response_model=LeadRead)
def update_lead_status(
    lead_id: UUID,
    status_data: LeadStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Update lead status."""
    lead = db.query(Lead).filter(Lead.id == lead_id).first()

    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    old_status = lead.status
    lead.status = status_data.status

    # Update timestamps based on status
    if status_data.status.value == "contacted" and not lead.contacted_at:
        lead.contacted_at = datetime.utcnow()
    elif status_data.status.value == "qualified" and not lead.qualified_at:
        lead.qualified_at = datetime.utcnow()
    elif status_data.status.value in ["won", "lost"] and not lead.closed_at:
        lead.closed_at = datetime.utcnow()

    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)

    # Convert to dict format
    lead_dict = {
        "id": lead.id,
        "name": lead.name,
        "email": lead.email,
        "phone": lead.phone,
        "source": lead.source,
        "location": lead.location,
        "metadata": lead._metadata if hasattr(lead, '_metadata') else {},
        "current_score": lead.current_score,
        "classification": lead.classification,
        "status": lead.status,
        "contacted_at": lead.contacted_at,
        "qualified_at": lead.qualified_at,
        "closed_at": lead.closed_at,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at,
    }
    return LeadRead.model_validate(lead_dict)
