"""Lead SQLAlchemy model definition."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import uuid4

from sqlalchemy import CheckConstraint, Column, DateTime, Enum, ForeignKey, Index, Integer, String, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
import enum


LeadClassification = Enum("hot", "warm", "cold", name="lead_classification")


class LeadStatus(str, enum.Enum):
    """Lead status enumeration."""

    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    PROPOSAL = "proposal"
    NEGOTIATION = "negotiation"
    WON = "won"
    LOST = "lost"


class Lead(Base):
    """Represents a sales lead tracked for scoring."""

    __tablename__ = "leads"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    source: Mapped[str] = mapped_column(String(100), nullable=False)
    location: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    current_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    classification: Mapped[Optional[str]] = mapped_column(LeadClassification, nullable=True)
    status: Mapped[LeadStatus] = mapped_column(SQLEnum(LeadStatus), default=LeadStatus.NEW, nullable=False)
    contacted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    qualified_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    # Track which user (sales rep) created this lead
    created_by: Mapped[Optional[uuid4]] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    # Map to 'metadata' column using private attribute to avoid SQLAlchemy reserved name conflict
    # Access via ._metadata in code, or use getattr/setattr with 'metadata' key
    _metadata: Mapped[Dict[str, Any]] = mapped_column("metadata", JSONB, default=dict, nullable=False)

    activities: Mapped[List["LeadActivity"]] = relationship(
        "LeadActivity", back_populates="lead", cascade="all, delete-orphan"
    )
    score_history: Mapped[List["LeadScoreHistory"]] = relationship(
        "LeadScoreHistory", back_populates="lead", cascade="all, delete-orphan"
    )
    assignments: Mapped[List["LeadAssignment"]] = relationship(
        "LeadAssignment", back_populates="lead", cascade="all, delete-orphan"
    )
    notes: Mapped[List["LeadNote"]] = relationship(
        "LeadNote", back_populates="lead", cascade="all, delete-orphan"
    )
    ai_scores: Mapped[List["LeadScore"]] = relationship(
        "LeadScore", back_populates="lead", cascade="all, delete-orphan"
    )
    engagement_events: Mapped[List["LeadEngagementEvent"]] = relationship(
        "LeadEngagementEvent", back_populates="lead", cascade="all, delete-orphan"
    )
    insights: Mapped[List["LeadInsight"]] = relationship(
        "LeadInsight", back_populates="lead", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("current_score >= 0 AND current_score <= 100", name="chk_leads_score_range"),
        Index("idx_leads_score", current_score.desc()),
        Index("idx_leads_classification", "classification"),
    )
    
    __mapper_args__ = {
        "exclude_properties": []  # Explicitly exclude nothing, but ensure _metadata is used
    }

    def __repr__(self) -> str:  # pragma: no cover - simple debug helper
        return f"Lead(id={self.id}, email={self.email}, score={self.current_score})"


from .activity import LeadActivity  # noqa: E402  # circular import for type checking
from .score_history import LeadScoreHistory  # noqa: E402
from .assignment import LeadAssignment  # noqa: E402
from .note import LeadNote  # noqa: E402
from .ai_scoring import LeadScore, LeadEngagementEvent, LeadInsight  # noqa: E402
