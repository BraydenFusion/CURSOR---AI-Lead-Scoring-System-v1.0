"""Note and notification-related Pydantic schemas."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class NoteBase(BaseModel):
    """Base note schema."""

    note_type: str = "general"
    content: str = Field(..., min_length=1, max_length=5000)


class NoteCreate(NoteBase):
    """Schema for creating a note."""

    lead_id: UUID


class NoteResponse(NoteBase):
    """Schema for note response."""

    id: UUID
    lead_id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    user_name: str | None = None  # For display

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    """Schema for notification response."""

    id: UUID
    notification_type: str
    title: str
    message: str
    link: str | None
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

