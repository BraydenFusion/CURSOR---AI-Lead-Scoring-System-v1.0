"""Background task scheduler for periodic email synchronization."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from fastapi import FastAPI

from app.services.email_sync import sync_all_email_accounts

logger = logging.getLogger(__name__)

SYNC_INTERVAL_SECONDS = 15 * 60  # 15 minutes


async def _email_sync_loop(stop_event: asyncio.Event) -> None:
    """Continuously run email sync until shutdown."""
    while not stop_event.is_set():
        try:
            await sync_all_email_accounts()
        except Exception as exc:  # pragma: no cover - log unexpected failures
            logger.exception("Scheduled email sync failed: %s", exc)
        await asyncio.wait(
            [stop_event.wait()],
            timeout=SYNC_INTERVAL_SECONDS,
        )


def start_email_sync_scheduler(app: FastAPI) -> None:
    """Register startup/shutdown handlers to manage the sync loop."""
    stop_event = asyncio.Event()
    task: Optional[asyncio.Task] = None

    @app.on_event("startup")
    async def _start_sync_loop() -> None:  # pragma: no cover - startup hook
        nonlocal task
        if task is None:
            logger.info("Starting email sync scheduler (interval=%ss)", SYNC_INTERVAL_SECONDS)
            task = asyncio.create_task(_email_sync_loop(stop_event))

    @app.on_event("shutdown")
    async def _stop_sync_loop() -> None:  # pragma: no cover - shutdown hook
        if task is not None:
            logger.info("Stopping email sync scheduler")
            stop_event.set()
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
