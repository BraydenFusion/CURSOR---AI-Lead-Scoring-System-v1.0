"""User-related Pydantic schemas for request/response validation."""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""

    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    full_name: str = Field(..., min_length=1, max_length=255)
    company_role: str | None = Field(None, max_length=100, description="User's role within their company")


class UserCreate(UserBase):
    """Schema for creating a new user with high security password requirements."""

    password: str = Field(..., min_length=12, max_length=128, description="Password must be at least 12 characters with uppercase, lowercase, number, and special character")
    role: UserRole = UserRole.SALES_REP


class UserLogin(BaseModel):
    """Schema for user login."""

    username: str
    password: str


class UserResponse(UserBase):
    """Schema for user response (excluding password)."""

    id: UUID
    role: UserRole
    is_active: bool
    created_at: datetime
    last_login: datetime | None = None
    profile_picture_url: str | None = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    """Schema for authentication token response."""

    access_token: str
    token_type: str
    user: UserResponse


class TokenData(BaseModel):
    """Schema for token payload data."""

    user_id: UUID | None = None
    username: str | None = None
    role: UserRole | None = None

