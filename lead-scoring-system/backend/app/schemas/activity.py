"""Pydantic schemas for lead activities."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ActivityBase(BaseModel):
    activity_type: str = Field(..., max_length=100)
    timestamp: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ActivityCreate(ActivityBase):
    lead_id: Optional[UUID] = None


class ActivityRead(ActivityBase):
    id: UUID
    lead_id: UUID
    points_awarded: int

    class Config:
        orm_mode = True
