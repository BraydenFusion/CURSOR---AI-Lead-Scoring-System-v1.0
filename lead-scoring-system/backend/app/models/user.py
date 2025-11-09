"""User SQLAlchemy model definition."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, String
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class UserRole(str, Enum):
    """User role enumeration."""

    ADMIN = "admin"
    MANAGER = "manager"
    SALES_REP = "sales_rep"


class User(Base):
    """Represents a system user with authentication and role."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    # Use SQLEnum to properly handle PostgreSQL ENUM type
    # The database has user_role ENUM type, so we need to use SQLEnum for proper casting
    role: Mapped[str] = mapped_column(
        SQLEnum(UserRole, name='user_role', create_type=False),
        nullable=False,
        server_default='sales_rep'  # Use lowercase string value directly
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    company_role: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    company_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    payment_plan: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    onboarding_completed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Relationships
    assigned_leads = relationship(
        "LeadAssignment",
        primaryjoin="User.id == LeadAssignment.user_id",
        back_populates="user",
        foreign_keys="[LeadAssignment.user_id]"
    )
    saved_reports = relationship(
        "SavedReport",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    email_accounts = relationship(
        "EmailAccount",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    def get_role_enum(self) -> UserRole:
        """Get role as UserRole enum."""
        try:
            return UserRole(self.role)
        except ValueError:
            return UserRole.SALES_REP

    def __repr__(self) -> str:  # pragma: no cover
        return f"User(id={self.id}, username={self.username}, role={self.role})"
