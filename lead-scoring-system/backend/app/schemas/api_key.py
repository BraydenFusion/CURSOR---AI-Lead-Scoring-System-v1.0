"""Pydantic schemas for API key management."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator

VALID_PERMISSIONS = {
    "read_leads",
    "write_leads",
    "read_activities",
    "write_activities",
    "read_assignments",
    "write_assignments",
}


class APIKeyBase(BaseModel):
    name: str = Field(..., max_length=150)
    permissions: List[str] = Field(default_factory=list)
    rate_limit: Optional[int] = Field(default=None, ge=1, le=10_000)

    @field_validator("permissions", mode="after")
    @classmethod
    def _validate_permissions(cls, value: List[str]) -> List[str]:
        invalid = [perm for perm in value if perm not in VALID_PERMISSIONS]
        if invalid:
            raise ValueError(f"Invalid permissions: {', '.join(invalid)}")
        return sorted(set(value))


class APIKeyCreate(APIKeyBase):
    pass


class APIKeyUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    permissions: Optional[List[str]] = None
    rate_limit: Optional[int] = Field(default=None, ge=1, le=10_000)
    active: Optional[bool] = None

    @field_validator("permissions", mode="after")
    @classmethod
    def _validate_permissions(cls, value: Optional[List[str]]) -> Optional[List[str]]:
        if value is None:
            return None
        invalid = [perm for perm in value if perm not in VALID_PERMISSIONS]
        if invalid:
            raise ValueError(f"Invalid permissions: {', '.join(invalid)}")
        return sorted(set(value))


class APIKeyRead(BaseModel):
    id: int
    name: str
    key_preview: str
    permissions: List[str]
    rate_limit: int
    created_at: datetime
    last_used: Optional[datetime]
    active: bool

    class Config:
        from_attributes = True


class APIKeySecretResponse(BaseModel):
    id: int
    name: str
    api_key: str
    key_preview: str
    permissions: List[str]
    rate_limit: int


class APIKeyListResponse(BaseModel):
    items: List[APIKeyRead]


class APIKeyUsageSample(BaseModel):
    timestamp: datetime
    requests: int


class APIKeyUsageResponse(BaseModel):
    key_id: int
    key_preview: str
    hourly_limit: int
    remaining: int
    reset_epoch: int
    samples: List[APIKeyUsageSample] = Field(default_factory=list)

