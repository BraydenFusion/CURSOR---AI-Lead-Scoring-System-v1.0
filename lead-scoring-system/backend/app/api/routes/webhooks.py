"""Webhook management routes."""

from __future__ import annotations

import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.api_key import Webhook, WebhookDelivery
from ...models.user import User
from ...schemas import (
    WebhookCreate,
    WebhookDeliveryListResponse,
    WebhookDeliveryRead,
    WebhookListResponse,
    WebhookRead,
    WebhookSecretResponse,
    WebhookTestRequest,
    WebhookUpdate,
)
from ...services.webhooks import trigger_webhook
from ...utils.auth import get_current_active_user

router = APIRouter(tags=["webhooks"])


def _serialize_webhook(record: Webhook) -> WebhookRead:
    return WebhookRead(
        id=record.id,
        url=record.url,
        events=list(record.events or []),
        active=record.active,
        created_at=record.created_at,
        updated_at=record.updated_at,
        secret_preview=record.secret_preview,
    )


def _get_webhook(db: Session, user: User, webhook_id: int) -> Webhook:
    webhook = (
        db.query(Webhook)
        .filter(Webhook.id == webhook_id)
        .filter(Webhook.user_id == user.id)
        .first()
    )
    if not webhook:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Webhook not found")
    return webhook


@router.get("/webhooks", response_model=WebhookListResponse)
def list_webhooks(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WebhookListResponse:
    records = (
        db.query(Webhook)
        .filter(Webhook.user_id == current_user.id)
        .order_by(Webhook.created_at.desc())
        .all()
    )
    return WebhookListResponse(items=[_serialize_webhook(record) for record in records])


@router.post("/webhooks", response_model=WebhookSecretResponse, status_code=status.HTTP_201_CREATED)
def create_webhook(
    payload: WebhookCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WebhookSecretResponse:
    secret = payload.secret or secrets.token_urlsafe(32)
    webhook = Webhook(
        user_id=current_user.id,
        url=str(payload.url),
        events=list(payload.events or []),
        secret=secret,
        active=payload.active if payload.active is not None else True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db.add(webhook)
    db.commit()
    db.refresh(webhook)
    return WebhookSecretResponse(webhook=_serialize_webhook(webhook), secret=secret)


@router.put("/webhooks/{webhook_id}", response_model=WebhookRead)
def update_webhook(
    webhook_id: int,
    payload: WebhookUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WebhookRead:
    webhook = _get_webhook(db, current_user, webhook_id)

    if payload.url is not None:
        webhook.url = str(payload.url)
    if payload.events is not None:
        webhook.events = list(payload.events)
    if payload.secret is not None:
        webhook.secret = payload.secret
    if payload.active is not None:
        webhook.active = payload.active
    webhook.updated_at = datetime.utcnow()

    db.add(webhook)
    db.commit()
    db.refresh(webhook)

    return _serialize_webhook(webhook)


@router.delete("/webhooks/{webhook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_webhook(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> None:
    webhook = _get_webhook(db, current_user, webhook_id)
    db.delete(webhook)
    db.commit()


@router.post("/webhooks/{webhook_id}/test", response_model=WebhookRead)
async def test_webhook(
    webhook_id: int,
    payload: WebhookTestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WebhookRead:
    webhook = _get_webhook(db, current_user, webhook_id)
    event = payload.event or "lead.test"
    sample_payload = payload.payload or {"message": "Test webhook delivery"}
    await trigger_webhook(event=event, payload=sample_payload, webhook_ids=[webhook.id])
    return _serialize_webhook(webhook)


@router.get("/webhooks/{webhook_id}/deliveries", response_model=WebhookDeliveryListResponse)
def list_webhook_deliveries(
    webhook_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WebhookDeliveryListResponse:
    _ = _get_webhook(db, current_user, webhook_id)
    deliveries = (
        db.query(WebhookDelivery)
        .filter(WebhookDelivery.webhook_id == webhook_id)
        .order_by(WebhookDelivery.created_at.desc())
        .limit(100)
        .all()
    )
    return WebhookDeliveryListResponse(
        webhook_id=webhook_id,
        deliveries=[
            WebhookDeliveryRead(
                id=delivery.id,
                event=delivery.event,
                status=delivery.status,
                response_code=delivery.response_code,
                error_message=delivery.error_message,
                created_at=delivery.created_at,
            )
            for delivery in deliveries
        ],
    )

