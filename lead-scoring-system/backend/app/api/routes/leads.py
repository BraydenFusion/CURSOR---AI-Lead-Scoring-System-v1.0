"""Lead-related API routes."""

from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Lead
from ...schemas import LeadCreate, LeadListResponse, LeadRead
from ...services.scoring_service import ScoringService


router = APIRouter()


@router.post("/", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_lead(payload: LeadCreate, db: Session = Depends(get_db)) -> Lead:
    """Create a new lead, calculate initial score, and return the record."""

    new_lead = Lead(
        name=payload.name,
        email=payload.email.lower(),
        phone=payload.phone,
        source=payload.source,
        location=payload.location,
        metadata=payload.metadata or {},
    )

    try:
        db.add(new_lead)
        db.commit()
        db.refresh(new_lead)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lead with this email already exists") from exc

    ScoringService.update_lead_score(db, new_lead.id)
    db.refresh(new_lead)

    return new_lead


@router.get("/", response_model=LeadListResponse)
def list_leads(
    sort: Literal["score", "date", "source"] = Query("score"),
    classification: Literal["all", "hot", "warm", "cold"] = Query("all"),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: str | None = Query(None, min_length=1),
    db: Session = Depends(get_db),
) -> LeadListResponse:
    """Return a paginated list of leads with filtering and sorting support."""

    query = db.query(Lead)

    if classification != "all":
        query = query.filter(Lead.classification == classification)

    if search:
        term = f"%{search.lower()}%"
        query = query.filter(
            (Lead.name.ilike(term))
            | (Lead.email.ilike(term))
            | (Lead.source.ilike(term))
        )

    if sort == "score":
        query = query.order_by(Lead.current_score.desc(), Lead.created_at.desc())
    elif sort == "date":
        query = query.order_by(Lead.created_at.desc())
    elif sort == "source":
        query = query.order_by(Lead.source.asc(), Lead.created_at.desc())

    total = query.count()
    offset = (page - 1) * per_page
    leads = query.offset(offset).limit(per_page).all()

    total_pages = max((total + per_page - 1) // per_page, 1)

    return LeadListResponse(
        leads=leads,
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/{lead_id}", response_model=LeadRead)
def get_lead(lead_id: UUID, db: Session = Depends(get_db)) -> Lead:
    """Retrieve lead details by identifier."""

    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if lead is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")

    return lead
