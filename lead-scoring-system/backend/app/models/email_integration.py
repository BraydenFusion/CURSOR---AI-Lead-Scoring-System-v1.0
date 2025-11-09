"""Email integration models for connected mailboxes and synced messages."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Boolean, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from ..utils.crypto import encrypt_string, decrypt_string, EncryptionUnavailable


class EmailAccount(Base):
    """Represents a connected email account (Gmail, Outlook, etc.)."""

    __tablename__ = "email_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)  # gmail | outlook
    email_address: Mapped[str] = mapped_column(String(255), nullable=False)
    _access_token: Mapped[str] = mapped_column("access_token", Text, nullable=False)
    _refresh_token: Mapped[Optional[str]] = mapped_column("refresh_token", Text, nullable=True)
    token_expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    last_sync: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    auto_sync_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user = relationship("User", back_populates="email_accounts")
    messages = relationship("EmailMessage", back_populates="email_account", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("email_address", "provider", name="uq_email_accounts_email_provider"),
        Index("ix_email_accounts_user_provider", "user_id", "provider"),
    )

    @property
    def access_token(self) -> str:
        return decrypt_string(self._access_token)

    @access_token.setter
    def access_token(self, value: str) -> None:
        self._access_token = encrypt_string(value)

    @property
    def refresh_token(self) -> Optional[str]:
        if self._refresh_token is None:
            return None
        return decrypt_string(self._refresh_token)

    @refresh_token.setter
    def refresh_token(self, value: Optional[str]) -> None:
        if value is None:
            self._refresh_token = None
        else:
            self._refresh_token = encrypt_string(value)

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"EmailAccount(id={self.id}, provider={self.provider}, email={self.email_address})"


class EmailMessage(Base):
    """Synced email message associated with a lead."""

    __tablename__ = "email_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("email_accounts.id", ondelete="CASCADE"), nullable=False)
    lead_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("leads.id", ondelete="SET NULL"), nullable=True)
    message_id: Mapped[str] = mapped_column(String(255), nullable=False)  # provider message ID
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    sender: Mapped[str] = mapped_column(String(255), nullable=False)
    recipients: Mapped[List[str]] = mapped_column(JSONB, nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    direction: Mapped[str] = mapped_column(String(20), nullable=False)  # sent | received
    read: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    email_account = relationship("EmailAccount", back_populates="messages")
    lead = relationship("Lead", back_populates="email_messages")

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"EmailMessage(id={self.id}, subject={self.subject}, direction={self.direction})"

