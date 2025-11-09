"""Schemas for webhook management."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator

WEBHOOK_EVENTS = {
    "lead.created",
    "lead.updated",
    "lead.scored",
    "lead.assigned",
    "lead.converted",
    "note.added",
    "activity.created",
}


class WebhookBase(BaseModel):
    url: HttpUrl
    events: List[str] = Field(default_factory=list)
    secret: Optional[str] = Field(default=None, min_length=16, max_length=255)
    active: Optional[bool] = True

    @field_validator("url", mode="after")
    @classmethod
    def _require_https(cls, value: HttpUrl) -> HttpUrl:
        if value.scheme != "https":
            raise ValueError("Webhook URL must use HTTPS")
        return value

    @field_validator("events", mode="after")
    @classmethod
    def _validate_events(cls, value: List[str]) -> List[str]:
        invalid = [event for event in value if event not in WEBHOOK_EVENTS and event != "*"]
        if invalid:
            raise ValueError(f"Invalid events: {', '.join(invalid)}")
        if not value:
            raise ValueError("At least one event must be selected")
        return sorted(set(value))


class WebhookCreate(WebhookBase):
    pass


class WebhookUpdate(BaseModel):
    url: Optional[HttpUrl] = None
    events: Optional[List[str]] = None
    secret: Optional[str] = Field(default=None, min_length=16, max_length=255)
    active: Optional[bool] = None

    @field_validator("url", mode="after")
    @classmethod
    def _require_https(cls, value: Optional[HttpUrl]) -> Optional[HttpUrl]:
        if value is not None and value.scheme != "https":
            raise ValueError("Webhook URL must use HTTPS")
        return value

    @field_validator("events", mode="after")
    @classmethod
    def _validate_events(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        invalid = [event for event in value if event not in WEBHOOK_EVENTS and event != "*"]
        if invalid:
            raise ValueError(f"Invalid events: {', '.join(invalid)}")
        if not value:
            raise ValueError("At least one event must be selected")
        return sorted(set(value))


class WebhookRead(BaseModel):
    id: int
    url: HttpUrl
    events: List[str]
    active: bool
    created_at: datetime
    updated_at: datetime
    secret_preview: str

    class Config:
        from_attributes = True


class WebhookListResponse(BaseModel):
    items: List[WebhookRead]


class WebhookTestRequest(BaseModel):
    event: Optional[str] = Field(default="lead.test")
    payload: Dict[str, Any] = Field(default_factory=dict)


class WebhookSecretResponse(BaseModel):
    webhook: WebhookRead
    secret: str


class WebhookDeliveryRead(BaseModel):
    id: int
    event: str
    status: str
    response_code: Optional[int]
    error_message: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class WebhookDeliveryListResponse(BaseModel):
    webhook_id: int
    deliveries: List[WebhookDeliveryRead]

