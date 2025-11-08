"""Lead score history SQLAlchemy model definition."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Index, Integer, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class LeadScoreHistory(Base):
    """Captures score changes over time for auditing and explanations."""

    __tablename__ = "lead_scores_history"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"))
    old_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    old_classification: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    new_classification: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    trigger_activity_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("lead_activities.id"), nullable=True
    )
    changed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="score_history")
    trigger_activity: Mapped[Optional["LeadActivity"]] = relationship(
        "LeadActivity", back_populates="trigger_for_scores"
    )

    __table_args__ = (Index("idx_scores_history_lead_id", "lead_id"),)

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return (
            "LeadScoreHistory(id={id}, lead_id={lead_id}, old={old}, new={new})".format(
                id=self.id, lead_id=self.lead_id, old=self.old_score, new=self.new_score
            )
        )


from .activity import LeadActivity  # noqa: E402  # circular import for type checking
from .lead import Lead  # noqa: E402
