"""Public API routes for lead management."""

from __future__ import annotations

import asyncio
from typing import List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from ....database import get_db
from ....models.activity import LeadActivity
from ....models.lead import Lead, LeadStatus
from ....schemas import (
    PublicActivityCreate,
    PublicLeadCreate,
    PublicLeadListResponse,
    PublicLeadResponse,
    PublicLeadUpdate,
)
from ....services.scoring_service import calculate_lead_score
from ....services.webhooks import trigger_webhook
from ...deps.api_key import APIKeyContext, ensure_permissions, get_api_key_context

router = APIRouter()


def _lead_to_response(lead: Lead) -> PublicLeadResponse:
    metadata = lead._metadata if hasattr(lead, "_metadata") else {}
    return PublicLeadResponse(
        id=lead.id,
        name=lead.name,
        email=lead.email,
        phone=lead.phone,
        source=lead.source,
        location=lead.location,
        metadata=metadata or {},
        current_score=lead.current_score,
        classification=lead.classification,
        status=lead.status.value if isinstance(lead.status, LeadStatus) else str(lead.status),
        created_at=lead.created_at,
        updated_at=lead.updated_at,
    )


def _fetch_lead_or_404(db: Session, lead_id: UUID, user_id: UUID) -> Lead:
    lead = (
        db.query(Lead)
        .filter(Lead.id == lead_id)
        .filter(Lead.created_by == user_id)
        .first()
    )
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return lead


@router.get("", response_model=PublicLeadListResponse)
def list_leads(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    score_min: Optional[int] = Query(default=None, ge=0, le=100),
    classification: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
    context: APIKeyContext = Depends(get_api_key_context),
) -> PublicLeadListResponse:
    ensure_permissions(context, ["read_leads"])

    query = db.query(Lead).filter(Lead.created_by == context.user.id)
    if score_min is not None:
        query = query.filter(Lead.current_score >= score_min)
    if classification:
        query = query.filter(Lead.classification == classification)

    total = query.count()
    leads: List[Lead] = (
        query.order_by(Lead.updated_at.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    return PublicLeadListResponse(
        items=[_lead_to_response(lead) for lead in leads],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.post("", response_model=PublicLeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(
    payload: PublicLeadCreate,
    db: Session = Depends(get_db),
    context: APIKeyContext = Depends(get_api_key_context),
) -> PublicLeadResponse:
    ensure_permissions(context, ["write_leads"])

    existing = db.query(Lead).filter(Lead.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Lead with this email already exists")

    lead = Lead(
        id=uuid4(),
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        source=payload.source or "api",
        location=payload.location,
        created_by=context.user.id,
        _metadata=payload.metadata or {},
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    try:
        from ....services.ai_scoring import calculate_overall_score

        calculate_overall_score(lead.id, db)
    except Exception:
        calculate_lead_score(lead.id, db)

    db.refresh(lead)

    response = _lead_to_response(lead)
    payload_dict = response.model_dump()

    asyncio.create_task(trigger_webhook(event="lead.created", payload=payload_dict))
    asyncio.create_task(trigger_webhook(event="lead.scored", payload=payload_dict))

    return response


@router.get("/{lead_id}", response_model=PublicLeadResponse)
def get_lead(
    lead_id: UUID,
    db: Session = Depends(get_db),
    context: APIKeyContext = Depends(get_api_key_context),
) -> PublicLeadResponse:
    ensure_permissions(context, ["read_leads"])
    lead = _fetch_lead_or_404(db, lead_id, context.user.id)
    return _lead_to_response(lead)


@router.put("/{lead_id}", response_model=PublicLeadResponse)
async def update_lead(
    lead_id: UUID,
    payload: PublicLeadUpdate,
    db: Session = Depends(get_db),
    context: APIKeyContext = Depends(get_api_key_context),
) -> PublicLeadResponse:
    ensure_permissions(context, ["write_leads"])

    lead = _fetch_lead_or_404(db, lead_id, context.user.id)

    if payload.email and payload.email != lead.email:
        exists = (
            db.query(func.count(Lead.id))
            .filter(Lead.email == payload.email)
            .filter(Lead.id != lead.id)
            .scalar()
        )
        if exists:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Another lead with this email exists")

    if payload.name is not None:
        lead.name = payload.name
    if payload.email is not None:
        lead.email = payload.email
    if payload.phone is not None:
        lead.phone = payload.phone
    if payload.source is not None:
        lead.source = payload.source
    if payload.location is not None:
        lead.location = payload.location
    if payload.metadata is not None:
        lead._metadata = payload.metadata
    if payload.status is not None:
        try:
            lead.status = LeadStatus(payload.status)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status value")

    db.add(lead)
    db.commit()

    calculate_lead_score(lead.id, db)
    db.refresh(lead)

    response = _lead_to_response(lead)
    asyncio.create_task(trigger_webhook(event="lead.updated", payload=response.model_dump()))
    asyncio.create_task(trigger_webhook(event="lead.scored", payload=response.model_dump()))
    return response


@router.post("/{lead_id}/activities", response_model=PublicLeadResponse, status_code=status.HTTP_201_CREATED)
async def create_activity(
    lead_id: UUID,
    payload: PublicActivityCreate,
    db: Session = Depends(get_db),
    context: APIKeyContext = Depends(get_api_key_context),
) -> PublicLeadResponse:
    ensure_permissions(context, ["write_activities", "read_leads"])

    lead = _fetch_lead_or_404(db, lead_id, context.user.id)

    activity = LeadActivity(
        lead_id=lead.id,
        activity_type=payload.activity_type,
        points_awarded=payload.points_awarded or 0,
        _metadata=payload.metadata or {},
    )
    db.add(activity)
    db.commit()

    calculate_lead_score(lead.id, db)
    db.refresh(lead)

    response = _lead_to_response(lead)
    event_payload = response.model_dump() | {"activity_id": str(activity.id), "activity_type": activity.activity_type}
    asyncio.create_task(trigger_webhook(event="activity.created", payload=event_payload))
    asyncio.create_task(trigger_webhook(event="lead.scored", payload=response.model_dump()))
    return response

