"""Pydantic schemas for email integrations and synced messages."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class EmailAccountRead(BaseModel):
    id: int
    provider: str
    email_address: str
    connected_at: datetime
    last_sync: Optional[datetime] = None
    auto_sync_enabled: bool = True

    class Config:
        from_attributes = True


class EmailMessageRead(BaseModel):
    id: int
    subject: str
    sender: str
    recipients: List[str]
    body_text: str
    sent_at: datetime
    direction: str
    read: bool

    class Config:
        from_attributes = True


class SendEmailRequest(BaseModel):
    email_account_id: int
    lead_id: UUID
    subject: str = Field(..., max_length=500)
    body: str
    recipients: Optional[List[str]] = None


class OAuthConnectResponse(BaseModel):
    authorization_url: str
    state: str


class OAuthCallbackResponse(BaseModel):
    success: bool
    email_account: EmailAccountRead

