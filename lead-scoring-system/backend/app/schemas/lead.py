"""Pydantic schemas for lead resources."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.lead import LeadStatus


class LeadBase(BaseModel):
    name: str = Field(..., max_length=255)
    email: str = Field(..., max_length=255)
    phone: Optional[str] = Field(None, max_length=50)
    source: str = Field(..., max_length=100)
    location: Optional[str] = Field(None, max_length=255)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class LeadCreate(LeadBase):
    pass


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    source: Optional[str] = None
    location: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class LeadRead(LeadBase):
    id: UUID
    current_score: int
    classification: Optional[str]
    status: LeadStatus
    contacted_at: Optional[datetime] = None
    qualified_at: Optional[datetime] = None
    closed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LeadListResponse(BaseModel):
    items: List[LeadRead]
    total: int
    page: int
    per_page: int


class LeadStatusUpdate(BaseModel):
    """Schema for updating lead status."""

    status: LeadStatus
