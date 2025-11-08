"""Lead Assignment SQLAlchemy model definition."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class LeadAssignment(Base):
    """Represents a lead assignment to a user."""

    __tablename__ = "lead_assignments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    assigned_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    assigned_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="active")  # active, completed, transferred
    notes: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)  # Primary assignee vs. team member

    # Relationships
    lead = relationship("Lead", back_populates="assignments")
    user = relationship("User", foreign_keys=[user_id], back_populates="assigned_leads")
    assigner = relationship("User", foreign_keys=[assigned_by])

    def __repr__(self) -> str:  # pragma: no cover
        return f"LeadAssignment(id={self.id}, lead_id={self.lead_id}, user_id={self.user_id}, status={self.status})"

