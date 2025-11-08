"""AI assistance routes for lead insights and email helpers."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    AIInsightResponse,
    EmailTemplateRequest,
    EmailTemplateResponse,
    NextBestActionResponse,
)
from app.services.ai_insights import (
    OpenAIUnavailableError,
    generate_email_template,
    generate_lead_insights,
    get_next_best_actions,
)
from app.utils.auth import get_current_active_user

router = APIRouter()


def _handle_ai_errors(error: Exception) -> None:
    if isinstance(error, OpenAIUnavailableError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI integration is not configured. Please add an API key.",
        ) from error
    if isinstance(error, ValueError):
        message = str(error) or "Unable to process AI request."
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message.lower() else status.HTTP_429_TOO_MANY_REQUESTS
        raise HTTPException(status_code=status_code, detail=message) from error
    raise HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail="Unexpected error while processing AI request.",
    ) from error


@router.get("/insights/{lead_id}", response_model=AIInsightResponse)
async def get_lead_insights(
    lead_id: UUID,
    db: Session = Depends(get_db),
    _: Any = Depends(get_current_active_user),
) -> AIInsightResponse:
    try:
        payload = await generate_lead_insights(db, lead_id)
        return AIInsightResponse.model_validate(payload)
    except Exception as error:  # pragma: no cover - raised via HTTPException
        _handle_ai_errors(error)


@router.post("/email-template", response_model=EmailTemplateResponse)
async def create_email_template(
    request: EmailTemplateRequest,
    db: Session = Depends(get_db),
    _: Any = Depends(get_current_active_user),
) -> EmailTemplateResponse:
    try:
        payload = await generate_email_template(db, request.lead_id, request.email_type)
        return EmailTemplateResponse.model_validate(payload)
    except Exception as error:  # pragma: no cover
        _handle_ai_errors(error)


@router.post("/next-best-action/{lead_id}", response_model=NextBestActionResponse)
async def next_best_action(
    lead_id: UUID,
    db: Session = Depends(get_db),
    _: Any = Depends(get_current_active_user),
) -> NextBestActionResponse:
    try:
        payload = await get_next_best_actions(db, lead_id)
        return NextBestActionResponse.model_validate(payload)
    except Exception as error:  # pragma: no cover
        _handle_ai_errors(error)

