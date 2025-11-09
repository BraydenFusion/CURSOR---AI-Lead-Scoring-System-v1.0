"""Webhook delivery utilities."""

from __future__ import annotations

import asyncio
import hmac
import hashlib
import json
import logging
import time
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional

import httpx
from sqlalchemy import or_

from ..database import SessionLocal
from ..models.api_key import Webhook, WebhookDelivery

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT_SECONDS = 10.0


def _serialize_payload(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, default=str, separators=(",", ":"), sort_keys=True)


def _compute_signature(secret: str, event: str, timestamp: str, payload_json: str) -> str:
    message = f"{timestamp}.{event}.{payload_json}".encode("utf-8")
    digest = hmac.new(secret.encode("utf-8"), message, hashlib.sha256).hexdigest()
    return digest


async def trigger_webhook(event: str, payload: Dict[str, Any], webhook_ids: Optional[List[int]] = None) -> None:
    """
    Trigger all active webhooks subscribed to the specified event.

    This function fetches active webhooks that listen for the event, signs the payload
    using the webhook secret, and delivers it with retry logic. Delivery attempts are
    recorded for auditing.
    """
    payload = payload or {}
    webhooks = _get_active_webhooks(event, webhook_ids=webhook_ids)
    if not webhooks:
        logger.debug("No webhooks registered for event %s", event)
        return

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        tasks = [
            _deliver_webhook(client=client, webhook=hook, event=event, payload=payload)
            for hook in webhooks
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for hook, result in zip(webhooks, results, strict=False):
            if isinstance(result, Exception):
                logger.warning("Webhook delivery failed for id=%s url=%s: %s", hook["id"], hook["url"], result)


def _get_active_webhooks(event: str, webhook_ids: Optional[List[int]] = None) -> List[Dict[str, Any]]:
    with SessionLocal() as session:
        query = session.query(Webhook).filter(Webhook.active.is_(True))
        if webhook_ids:
            query = query.filter(Webhook.id.in_(webhook_ids))
        records: Iterable[Webhook] = query.filter(
            or_(Webhook.events.contains([event]), Webhook.events.contains(["*"]))
        ).all()
        webhooks: List[Dict[str, Any]] = [
            {
                "id": record.id,
                "user_id": str(record.user_id),
                "url": record.url,
                "secret": record.secret,
                "events": list(record.events or []),
            }
            for record in records
        ]
        return webhooks


async def _deliver_webhook(
    client: httpx.AsyncClient,
    webhook: Dict[str, Any],
    event: str,
    payload: Dict[str, Any],
) -> None:
    payload_json = _serialize_payload(payload)
    attempts = 0
    error_message: Optional[str] = None
    response_code: Optional[int] = None
    response_body: Optional[str] = None
    duration_ms: Optional[int] = None

    while attempts < MAX_RETRIES:
        attempts += 1
        timestamp = str(int(time.time()))
        signature = _compute_signature(webhook["secret"], event, timestamp, payload_json)
        headers = {
            "Content-Type": "application/json",
            "X-Event": event,
            "X-Signature": signature,
            "X-Timestamp": timestamp,
        }

        start = time.perf_counter()
        try:
            response = await client.post(webhook["url"], headers=headers, content=payload_json)
            duration_ms = int((time.perf_counter() - start) * 1000)
            response_code = response.status_code
            response_body = response.text[:2000] if response.text else None
            if response.status_code < 500:
                status = "success" if response.status_code < 400 else "failed"
                error_message = None if status == "success" else response.text[:500]
                _record_delivery(
                    webhook_id=webhook["id"],
                    event=event,
                    status=status,
                    response_code=response_code,
                    error_message=error_message,
                    response_body=response_body,
                    duration_ms=duration_ms,
                )
                return
        except httpx.RequestError as exc:
            duration_ms = int((time.perf_counter() - start) * 1000)
            error_message = str(exc)
            logger.warning(
                "Webhook request error for id=%s url=%s attempt=%s: %s",
                webhook["id"],
                webhook["url"],
                attempts,
                exc,
            )

        await asyncio.sleep(2** attempts / 4)  # incremental backoff

    _record_delivery(
        webhook_id=webhook["id"],
        event=event,
        status="failed",
        response_code=response_code,
        error_message=error_message or "Exceeded retry attempts",
        response_body=response_body,
        duration_ms=duration_ms,
    )


def _record_delivery(
    *,
    webhook_id: int,
    event: str,
    status: str,
    response_code: Optional[int],
    error_message: Optional[str],
    response_body: Optional[str],
    duration_ms: Optional[int],
) -> None:
    with SessionLocal() as session:
        delivery = WebhookDelivery(
            webhook_id=webhook_id,
            event=event,
            status=status,
            response_code=response_code,
            error_message=error_message,
            response_body=response_body,
            duration_ms=duration_ms,
            created_at=datetime.utcnow(),
        )
        session.add(delivery)
        session.commit()


def verify_webhook_signature(
    *,
    secret: str,
    signature: str,
    timestamp: str,
    event: str,
    payload: Any,
    tolerance_seconds: int = 300,
) -> bool:
    """
    Verify the webhook signature received from an external webhook consumer.
    """
    if not signature or not timestamp:
        return False

    try:
        ts = int(timestamp)
    except ValueError:
        return False

    now = int(time.time())
    if abs(now - ts) > tolerance_seconds:
        return False

    if isinstance(payload, (bytes, bytearray)):
        payload_json = payload.decode("utf-8")
    elif isinstance(payload, str):
        payload_json = payload
    else:
        payload_json = _serialize_payload(payload)

    expected = _compute_signature(secret, event, timestamp, payload_json)
    return hmac.compare_digest(expected, signature)

