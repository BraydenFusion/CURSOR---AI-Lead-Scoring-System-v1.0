"""Assignment rule model for auto lead distribution."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class AssignmentRule(Base):
    """Represents an automated assignment rule used to distribute leads."""

    __tablename__ = "assignment_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    rule_type: Mapped[str] = mapped_column(String(50), nullable=False)
    conditions: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    assignment_logic: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    created_by_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    created_by = relationship("User", foreign_keys=[created_by_id])

    __table_args__ = (
        CheckConstraint("priority >= 1 AND priority <= 10", name="chk_assignment_rules_priority_range"),
    )

    def __repr__(self) -> str:  # pragma: no cover - debugging only
        return f"AssignmentRule(id={self.id}, name={self.name}, active={self.active}, priority={self.priority})"

