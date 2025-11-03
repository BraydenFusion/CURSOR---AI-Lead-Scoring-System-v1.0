"""AI scoring related SQLAlchemy models."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import uuid4

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class LeadScore(Base):
    """Stores detailed AI scoring results for leads."""

    __tablename__ = "lead_scores"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    overall_score: Mapped[int] = mapped_column(Integer, nullable=False)
    engagement_score: Mapped[int] = mapped_column(Integer, nullable=False)
    buying_signal_score: Mapped[int] = mapped_column(Integer, nullable=False)
    demographic_score: Mapped[int] = mapped_column(Integer, nullable=False)
    priority_tier: Mapped[str] = mapped_column(String(10), nullable=False)  # 'HOT', 'WARM', 'COLD'
    confidence_level: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    scoring_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB(), nullable=True)
    scored_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="ai_scores")

    __table_args__ = (
        CheckConstraint("overall_score >= 0 AND overall_score <= 100", name="chk_lead_scores_overall"),
        CheckConstraint("engagement_score >= 0 AND engagement_score <= 100", name="chk_lead_scores_engagement"),
        CheckConstraint("buying_signal_score >= 0 AND buying_signal_score <= 100", name="chk_lead_scores_buying"),
        CheckConstraint("demographic_score >= 0 AND demographic_score <= 100", name="chk_lead_scores_demographic"),
        CheckConstraint("confidence_level >= 0.00 AND confidence_level <= 1.00", name="chk_lead_scores_confidence"),
        Index("idx_lead_scores_lead_id", "lead_id"),
        Index("idx_lead_scores_overall_score", "overall_score"),
        Index("idx_lead_scores_priority_tier", "priority_tier"),
        Index("idx_lead_scores_scored_at", "scored_at"),
    )


class LeadEngagementEvent(Base):
    """Tracks engagement events for scoring calculations."""

    __tablename__ = "lead_engagement_events"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    event_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'email_open', 'website_visit', etc.
    event_data: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSONB(), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="engagement_events")

    __table_args__ = (
        Index("idx_engagement_events_lead_id", "lead_id"),
        Index("idx_engagement_events_type", "event_type"),
        Index("idx_engagement_events_created_at", "created_at"),
    )


class LeadInsight(Base):
    """Stores AI-generated insights and talking points for leads."""

    __tablename__ = "lead_insights"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    lead_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), ForeignKey("leads.id", ondelete="CASCADE"), nullable=False)
    insight_type: Mapped[str] = mapped_column(String(50), nullable=False)  # 'talking_point', 'concern', 'opportunity'
    content: Mapped[str] = mapped_column(Text(), nullable=False)
    confidence: Mapped[float] = mapped_column(Numeric(3, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    lead: Mapped["Lead"] = relationship("Lead", back_populates="insights")

    __table_args__ = (
        CheckConstraint("confidence >= 0.00 AND confidence <= 1.00", name="chk_lead_insights_confidence"),
        Index("idx_lead_insights_lead_id", "lead_id"),
        Index("idx_lead_insights_type", "insight_type"),
        Index("idx_lead_insights_created_at", "created_at"),
    )


from .lead import Lead  # noqa: E402  # circular import for type checking

