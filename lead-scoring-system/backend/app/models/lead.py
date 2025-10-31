"""Lead SQLAlchemy model definition."""

from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


LeadClassification = Enum("hot", "warm", "cold", name="lead_classification")


class Lead(Base):
    """Represents a sales lead tracked for scoring."""

    __tablename__ = "leads"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)
    current_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    classification: Mapped[str] = mapped_column(LeadClassification, default="cold", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    metadata: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)

    activities: Mapped[List["LeadActivity"]] = relationship(
        "LeadActivity", back_populates="lead", cascade="all, delete-orphan"
    )
    score_history: Mapped[List["LeadScoreHistory"]] = relationship(
        "LeadScoreHistory", back_populates="lead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("current_score >= 0 AND current_score <= 100", name="chk_leads_score_range"),
        Index("idx_leads_score", current_score.desc()),
        Index("idx_leads_classification", "classification"),
    )

    def __repr__(self) -> str:  # pragma: no cover - simple debug helper
        return f"Lead(id={self.id}, email={self.email}, score={self.current_score})"


from .activity import LeadActivity  # noqa: E402  # circular import for type checking
from .score_history import LeadScoreHistory  # noqa: E402
