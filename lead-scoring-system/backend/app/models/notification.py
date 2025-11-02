"""Notification SQLAlchemy model definition."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from sqlalchemy import Boolean, DateTime, Enum as SQLEnum, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class NotificationType(str, Enum):
    """Notification type enumeration."""

    LEAD_ASSIGNED = "lead_assigned"
    LEAD_HOT = "lead_hot"
    LEAD_UPDATED = "lead_updated"
    ACTIVITY_ADDED = "activity_added"
    NOTE_ADDED = "note_added"


class Notification(Base):
    """Represents a notification for a user."""

    __tablename__ = "notifications"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    user_id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    notification_type: Mapped[NotificationType] = mapped_column(SQLEnum(NotificationType), nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    link: Mapped[str | None] = mapped_column(String(255), nullable=True)  # Link to related resource
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User")

    def __repr__(self) -> str:  # pragma: no cover
        return f"Notification(id={self.id}, user_id={self.user_id}, type={self.notification_type.value})"

