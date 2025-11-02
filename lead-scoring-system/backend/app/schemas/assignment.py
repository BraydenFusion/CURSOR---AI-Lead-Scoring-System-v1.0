"""Assignment-related Pydantic schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class AssignmentCreate(BaseModel):
    """Schema for creating a new lead assignment."""

    lead_id: UUID
    user_id: UUID
    notes: str | None = Field(None, max_length=500)
    is_primary: bool = True


class AssignmentResponse(BaseModel):
    """Schema for assignment response."""

    id: UUID
    lead_id: UUID
    user_id: UUID
    assigned_by: UUID | None
    assigned_at: datetime
    status: str
    notes: str | None
    is_primary: bool

    class Config:
        from_attributes = True


class AssignmentWithDetails(AssignmentResponse):
    """Schema for assignment response with related entity details."""

    lead_name: str
    lead_email: str
    lead_score: int
    user_name: str
    user_email: str

