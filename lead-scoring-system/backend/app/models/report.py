"""Report model for saved analytics configurations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import Integer

from ..database import Base


class SavedReport(Base):
    """Represents a saved analytics report configuration."""

    __tablename__ = "saved_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    report_type: Mapped[str] = mapped_column(String(50), default="custom", nullable=False)
    filters: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    metrics: Mapped[List[str]] = mapped_column(JSONB, default=list, nullable=False)
    schedule: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, nullable=False
    )
    last_run: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="saved_reports")

    def requires_email_delivery(self) -> bool:
        """Return True if the report has a schedule that should trigger email delivery."""
        return self.schedule is not None and self.schedule.lower() != "manual"


