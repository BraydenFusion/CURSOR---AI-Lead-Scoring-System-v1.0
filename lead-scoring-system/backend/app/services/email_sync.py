"""Email synchronization and sending helpers for Gmail and Outlook integrations."""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import EmailAccount, EmailMessage, Lead, LeadActivity
from app.utils.crypto import EncryptionUnavailable

logger = logging.getLogger(__name__)


@dataclass
class ProviderMessage:
    """Lightweight structure representing an email retrieved from a provider."""

    message_id: str
    subject: str
    sender: str
    recipients: List[str]
    body_text: str
    sent_at: datetime
    direction: str  # "sent" | "received"
    read: bool = True
    lead_email: Optional[str] = None
    engagement_event: Optional[str] = None  # open | click | reply


# ---------------------------------------------------------------------------
# Public APIs
# ---------------------------------------------------------------------------

async def sync_gmail_emails(user_id: UUID) -> int:
    """Sync Gmail messages for the given user.

    Returns the number of messages processed.
    """
    logger.info("Starting Gmail sync for user %s", user_id)
    return await _sync_provider_messages(user_id, provider="gmail", fetcher=_fetch_gmail_messages)


async def sync_outlook_emails(user_id: UUID) -> int:
    """Sync Outlook messages for the given user.

    Returns the number of messages processed.
    """
    logger.info("Starting Outlook sync for user %s", user_id)
    return await _sync_provider_messages(user_id, provider="outlook", fetcher=_fetch_outlook_messages)


async def send_email_via_integration(
    email_account_id: int,
    lead_id: UUID,
    subject: str,
    body: str,
    recipients: Optional[List[str]] = None,
) -> EmailMessage:
    """Send an email through a connected account and record the message."""
    with SessionLocal() as db:
        account = (
            db.query(EmailAccount)
            .filter(EmailAccount.id == email_account_id)
            .options()
            .one_or_none()
        )
        if not account:
            raise ValueError("Email account not found.")

        lead = db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if not lead:
            raise ValueError("Lead not found.")

        try:
            access_token = account.access_token
        except EncryptionUnavailable as exc:
            raise RuntimeError("Unable to send email: encryption key not configured.") from exc

        recipient_list = recipients or [lead.email]
        if not recipient_list:
            raise ValueError("No recipients specified for email.")

        # Placeholder for actual provider API call
        if account.provider == "gmail":
            await _send_via_gmail(access_token, account.email_address, recipient_list, subject, body)
        elif account.provider == "outlook":
            await _send_via_outlook(access_token, account.email_address, recipient_list, subject, body)
        else:
            raise ValueError(f"Unsupported provider {account.provider}")

        message = EmailMessage(
            email_account_id=account.id,
            lead_id=lead.id,
            message_id=_generate_local_message_id(),
            subject=subject,
            sender=account.email_address,
            recipients=recipient_list,
            body_text=body,
            sent_at=datetime.utcnow(),
            direction="sent",
            read=True,
        )
        db.add(message)
        _record_lead_email_activity(db, lead, message, engagement_event=None)

        db.commit()
        db.refresh(message)
        logger.info("Sent email via %s for lead %s", account.provider, lead_id)
        return message


# ---------------------------------------------------------------------------
# Core synchronization helpers
# ---------------------------------------------------------------------------

async def _sync_provider_messages(
    user_id: UUID,
    *,
    provider: str,
    fetcher,
) -> int:
    """Common entry point for fetching and persisting provider messages."""
    processed = 0
    with SessionLocal() as db:
        account = (
            db.query(EmailAccount)
            .filter(EmailAccount.user_id == user_id, EmailAccount.provider == provider)
            .one_or_none()
        )
        if not account:
            logger.info("No %s account connected for user %s", provider, user_id)
            return 0

        since = account.last_sync or datetime.utcnow() - timedelta(days=7)

        try:
            access_token = account.access_token
        except EncryptionUnavailable:
            logger.warning("Email encryption key missing; cannot sync %s for user %s", provider, user_id)
            return 0

        messages = await fetcher(account, since=since, access_token=access_token)
        if not messages:
            logger.info("No new %s messages for user %s", provider, user_id)
            account.last_sync = datetime.utcnow()
            db.add(account)
            db.commit()
            return 0

        for message in messages:
            if _message_exists(db, account.id, message.message_id):
                continue
            lead = _match_lead(db, message, default_lead=account.user_id)
            lead_id = lead.id if lead else None
            db_message = EmailMessage(
                email_account_id=account.id,
                lead_id=lead_id,
                message_id=message.message_id,
                subject=message.subject,
                sender=message.sender,
                recipients=message.recipients,
                body_text=message.body_text,
                sent_at=message.sent_at,
                direction=message.direction,
                read=message.read,
            )
            db.add(db_message)
            if lead:
                _record_lead_email_activity(db, lead, db_message, engagement_event=message.engagement_event)
            processed += 1

        account.last_sync = datetime.utcnow()
        db.add(account)
        db.commit()
        logger.info("Processed %s new %s messages for user %s", processed, provider, user_id)
    return processed


def _message_exists(db: Session, account_id: int, message_id: str) -> bool:
    return (
        db.query(EmailMessage.id)
        .filter(EmailMessage.email_account_id == account_id, EmailMessage.message_id == message_id)
        .first()
        is not None
    )


def _match_lead(db: Session, message: ProviderMessage, default_lead: Optional[UUID] = None) -> Optional[Lead]:
    """Attempt to associate an email with a lead based on email addresses."""
    addresses = set(message.recipients + [message.sender])
    if message.lead_email:
        addresses.add(message.lead_email)

    lead = (
        db.query(Lead)
        .filter(Lead.email.in_(addresses))
        .order_by(Lead.created_at.desc())
        .first()
    )
    return lead


def _record_lead_email_activity(
    db: Session,
    lead: Lead,
    message: EmailMessage,
    engagement_event: Optional[str],
) -> None:
    """Persist activity and adjust engagement metrics on a lead."""
    activity = LeadActivity(
        lead_id=lead.id,
        activity_type="email_sync",
        timestamp=message.sent_at,
        points_awarded=0,
        _metadata={
            "subject": message.subject,
            "direction": message.direction,
            "sender": message.sender,
            "recipients": message.recipients,
        },
    )
    db.add(activity)

    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    engagement = metadata.setdefault("email_engagement", {"opens": 0, "clicks": 0, "replies": 0})

    if engagement_event == "open":
        engagement["opens"] = engagement.get("opens", 0) + 1
    elif engagement_event == "click":
        engagement["clicks"] = engagement.get("clicks", 0) + 1
    elif engagement_event == "reply" or message.direction == "received":
        engagement["replies"] = engagement.get("replies", 0) + 1

    metadata["email_engagement"] = engagement
    lead._metadata = metadata
    db.add(lead)


# ---------------------------------------------------------------------------
# Provider fetch/send implementations (placeholders)
# ---------------------------------------------------------------------------

async def _fetch_gmail_messages(account: EmailAccount, *, since: datetime, access_token: str) -> List[ProviderMessage]:
    """Fetch Gmail messages using Gmail API (placeholder)."""
    # TODO: Implement Gmail API integration.
    logger.debug(
        "Fetching Gmail messages for %s since %s (placeholder implementation)",
        account.email_address,
        since.isoformat(),
    )
    await asyncio.sleep(0)  # Yield control
    return []


async def _fetch_outlook_messages(account: EmailAccount, *, since: datetime, access_token: str) -> List[ProviderMessage]:
    """Fetch Outlook messages using Microsoft Graph API (placeholder)."""
    # TODO: Implement Outlook API integration.
    logger.debug(
        "Fetching Outlook messages for %s since %s (placeholder implementation)",
        account.email_address,
        since.isoformat(),
    )
    await asyncio.sleep(0)
    return []


async def _send_via_gmail(access_token: str, sender: str, recipients: List[str], subject: str, body: str) -> None:
    """Send email via Gmail API (placeholder)."""
    # TODO: Implement Gmail send functionality.
    logger.debug("Sending Gmail message from %s to %s (placeholder)", sender, recipients)
    await asyncio.sleep(0)


async def _send_via_outlook(access_token: str, sender: str, recipients: List[str], subject: str, body: str) -> None:
    """Send email via Outlook Graph API (placeholder)."""
    # TODO: Implement Outlook send functionality.
    logger.debug("Sending Outlook message from %s to %s (placeholder)", sender, recipients)
    await asyncio.sleep(0)


def _generate_local_message_id() -> str:
    """Generate a pseudo message ID for locally sent emails (until provider echoes a real ID)."""
    return f"local-{datetime.utcnow().timestamp()}"


# ---------------------------------------------------------------------------
# Batch utilities
# ---------------------------------------------------------------------------

async def sync_all_email_accounts() -> None:
    """Iterate over all accounts and trigger provider-specific syncs."""
    logger.info("Running scheduled email sync for all accounts")
    with SessionLocal() as db:
        accounts: Iterable[EmailAccount] = db.query(EmailAccount).filter(EmailAccount.auto_sync_enabled.is_(True)).all()

    tasks = []
    for account in accounts:
        if account.provider == "gmail":
            tasks.append(sync_gmail_emails(account.user_id))
        elif account.provider == "outlook":
            tasks.append(sync_outlook_emails(account.user_id))

    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Scheduled email sync completed")

