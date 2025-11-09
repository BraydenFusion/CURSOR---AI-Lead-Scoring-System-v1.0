"""Background scheduler that runs CRM syncs on a cadence."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from fastapi import FastAPI

from app.config import get_settings
from app.database import SessionLocal
from app.models import CRMIntegration
from app.services.crm_sync import (
    sync_from_pipedrive,
    sync_to_pipedrive,
)

logger = logging.getLogger(__name__)
settings = get_settings()

FREQUENCY_SECONDS: Dict[str, int] = {
    "manual": 0,
    "hourly": 3600,
    "daily": 86400,
}


async def _crm_sync_loop(stop_event: asyncio.Event) -> None:
    """Periodically evaluate which integrations should be synced."""
    interval = settings.crm_sync_interval_seconds or 900
    logger.info("CRM scheduler started (interval=%ss)", interval)
    while not stop_event.is_set():
        try:
            await _sync_due_integrations()
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.exception("CRM scheduled sync failed: %s", exc)
        await asyncio.wait([stop_event.wait()], timeout=interval)


async def _sync_due_integrations() -> None:
    now = datetime.utcnow()
    with SessionLocal() as db:
        integrations = (
            db.query(CRMIntegration)
            .filter(CRMIntegration.active.is_(True), CRMIntegration.sync_frequency != "manual")
            .all()
        )

        for integration in integrations:
            frequency_seconds = FREQUENCY_SECONDS.get(integration.sync_frequency, 0)
            if frequency_seconds <= 0:
                continue

            if integration.last_sync:
                elapsed = (now - integration.last_sync).total_seconds()
                if elapsed < frequency_seconds:
                    continue

            logger.info(
                "Scheduled CRM sync for integration %s (%s, direction=%s)",
                integration.id,
                integration.provider,
                integration.sync_direction,
            )

            await _run_integration_sync(integration.id, integration.provider, integration.sync_direction)


async def _run_integration_sync(integration_id: int, provider: str, direction: str) -> None:
    async with _session_scope() as session:
        if provider == "pipedrive":
            if direction in ("to_crm", "bidirectional"):
                await sync_to_pipedrive(integration_id, db=session)
            if direction in ("from_crm", "bidirectional"):
                await sync_from_pipedrive(integration_id, db=session)
        else:
            logger.warning("Unknown CRM provider %s for integration %s", provider, integration_id)


def start_crm_sync_scheduler(app: FastAPI) -> None:
    """Attach scheduler startup/shutdown hooks to the FastAPI app."""
    stop_event = asyncio.Event()
    task: Optional[asyncio.Task] = None

    @app.on_event("startup")
    async def _startup() -> None:  # pragma: no cover
        nonlocal task
        if task is None:
            task = asyncio.create_task(_crm_sync_loop(stop_event))

    @app.on_event("shutdown")
    async def _shutdown() -> None:  # pragma: no cover
        if task is not None:
            stop_event.set()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass


class _session_scope:
    """Async context manager for DB sessions outside of request lifecycle."""

    def __init__(self) -> None:
        self.session = None

    async def __aenter__(self):
        self.session = SessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc, tb):
        if self.session is None:
            return
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

