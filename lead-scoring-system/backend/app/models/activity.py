"""Lead activity SQLAlchemy model definition."""

from datetime import datetime
from typing import Any, Dict
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class LeadActivity(Base):
    """Represents an interaction or activity associated with a lead."""

    __tablename__ = "lead_activities"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    activity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    points_awarded: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    # Map to 'metadata' column using private attribute to avoid SQLAlchemy reserved name conflict
    # Access via ._metadata in code
    _metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="activities")
    trigger_for_scores: Mapped[list["LeadScoreHistory"]] = relationship(
        "LeadScoreHistory", back_populates="trigger_activity"
    )

    __table_args__ = (
        Index("idx_activities_lead_id", "lead_id"),
        Index("idx_activities_timestamp", timestamp.desc()),
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"LeadActivity(id={self.id}, type={self.activity_type}, points={self.points_awarded})"


from .lead import Lead  # noqa: E402  # circular import for type checking
from .score_history import LeadScoreHistory  # noqa: E402
