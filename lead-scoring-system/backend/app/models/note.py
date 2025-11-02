"""Lead Note SQLAlchemy model definition."""

from datetime import datetime
from uuid import uuid4

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class LeadNote(Base):
    """Represents a note attached to a lead."""

    __tablename__ = "lead_notes"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    note_type: Mapped[str] = mapped_column(String(50), default="general")  # general, call, email, meeting, etc.
    content: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    # Relationships
    lead = relationship("Lead", back_populates="notes")
    user = relationship("User")

    def __repr__(self) -> str:  # pragma: no cover
        return f"LeadNote(id={self.id}, lead_id={self.lead_id}, note_type={self.note_type})"

