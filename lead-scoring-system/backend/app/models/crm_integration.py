"""CRM integration models for Pipedrive sync."""

from __future__ import annotations

import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..utils.crypto import decrypt_string, encrypt_string


class CRMIntegration(Base):
    """Represents a connected CRM provider (Pipedrive)."""

    __tablename__ = "crm_integrations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # pipedrive
    _credentials: Mapped[str] = mapped_column("credentials", Text, nullable=False)
    sync_direction: Mapped[str] = mapped_column(String(20), nullable=False, default="bidirectional")  # to_crm | from_crm | bidirectional
    field_mappings: Mapped[Dict[str, Any]] = mapped_column(JSONB, default=dict, nullable=False)
    sync_frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")  # manual | hourly | daily
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    conflict_strategy: Mapped[str] = mapped_column(String(20), nullable=False, default="manual")  # manual | prefer_crm | prefer_local
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    user = relationship("User", back_populates="crm_integrations")
    logs = relationship("SyncLog", back_populates="integration", cascade="all, delete-orphan")

    @property
    def credentials(self) -> Dict[str, Any]:
        decrypted = decrypt_string(self._credentials)
        return json.loads(decrypted)

    @credentials.setter
    def credentials(self, value: Dict[str, Any]) -> None:
        self._credentials = encrypt_string(json.dumps(value))

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"CRMIntegration(id={self.id}, provider={self.provider}, active={self.active})"


class SyncLog(Base):
    """Tracks CRM sync executions and their outcomes."""

    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    integration_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("crm_integrations.id", ondelete="CASCADE"),
        nullable=False,
    )
    sync_started: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    sync_completed: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    records_synced: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    errors: Mapped[Optional[List[Dict[str, Any]]]] = mapped_column(JSONB, nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="running")  # running | success | partial | failed
    direction: Mapped[str] = mapped_column(String(20), nullable=False, default="bidirectional")

    integration = relationship("CRMIntegration", back_populates="logs")

    def mark_completed(self, *, records: int, status: str, errors: Optional[List[Dict[str, Any]]] = None) -> None:
        self.sync_completed = datetime.utcnow()
        self.records_synced = records
        self.status = status
        self.errors = errors

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"SyncLog(id={self.id}, provider={self.integration.provider if self.integration else 'unknown'}, status={self.status})"

