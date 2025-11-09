"""Schemas for the public API v1 endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, RootModel


class PublicLeadMetadata(RootModel[Dict[str, Any]]):
    @property
    def data(self) -> Dict[str, Any]:
        return dict(self.root)


class PublicLeadCreate(BaseModel):
    name: str = Field(..., max_length=255)
    email: EmailStr
    phone: Optional[str] = Field(default=None, max_length=50)
    source: str = Field(default="api", max_length=100)
    location: Optional[str] = Field(default=None, max_length=255)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PublicLeadUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=50)
    source: Optional[str] = Field(default=None, max_length=100)
    location: Optional[str] = Field(default=None, max_length=255)
    metadata: Optional[Dict[str, Any]] = None
    status: Optional[str] = Field(default=None, description="Lead status value")


class PublicLeadResponse(BaseModel):
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    source: str
    location: Optional[str]
    metadata: Dict[str, Any]
    current_score: int
    classification: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PublicLeadListResponse(BaseModel):
    items: List[PublicLeadResponse]
    total: int
    limit: int
    offset: int


class PublicActivityCreate(BaseModel):
    activity_type: str = Field(..., max_length=100)
    notes: Optional[str] = Field(default=None, max_length=1000)
    points_awarded: Optional[int] = Field(default=0, ge=0, le=100)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PublicUserInfo(BaseModel):
    user_id: UUID
    email: EmailStr
    full_name: str
    role: str
    api_key_permissions: List[str]
    api_key_rate_limit: int
    api_key_remaining: int
    api_key_reset_epoch: int

