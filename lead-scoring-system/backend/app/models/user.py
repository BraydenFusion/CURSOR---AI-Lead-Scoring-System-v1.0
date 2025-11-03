"""User SQLAlchemy model definition."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, Enum as SQLEnum, String
from sqlalchemy.dialects.postgresql import UUID
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

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(SQLEnum(UserRole), nullable=False, default=UserRole.SALES_REP)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    last_login: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Relationships
    assigned_leads = relationship(
        "LeadAssignment",
        primaryjoin="User.id == LeadAssignment.user_id",
        back_populates="user"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"User(id={self.id}, username={self.username}, role={self.role.value})"

