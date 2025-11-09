"""CRM synchronization helpers for Salesforce and HubSpot."""

from __future__ import annotations

import asyncio
import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional, Tuple

from hubspot import HubSpot  # type: ignore
from simple_salesforce import Salesforce  # type: ignore
from sqlalchemy.orm import Session
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential

from app.config import get_settings
from app.database import SessionLocal
from app.models import CRMIntegration, Lead, SyncLog
from app.services.scoring_service import calculate_lead_score

logger = logging.getLogger(__name__)
settings = get_settings()


class CRMRateLimitError(RuntimeError):
    """Raised when a CRM responds with a rate-limit status."""


class CRMAuthError(RuntimeError):
    """Raised when authentication to the CRM fails."""


SyncResult = Tuple[int, List[Dict[str, Any]]]


async def sync_to_salesforce(integration_id: int, *, db: Session | None = None) -> SyncResult:
    """Push new or updated leads to Salesforce."""
    return await _run_sync(
        integration_id=integration_id,
        direction="to_crm",
        handler=_push_salesforce,
        db=db,
    )


async def sync_from_salesforce(integration_id: int, *, db: Session | None = None) -> SyncResult:
    """Pull new or updated Salesforce contacts/leads."""
    return await _run_sync(
        integration_id=integration_id,
        direction="from_crm",
        handler=_pull_salesforce,
        db=db,
    )


async def sync_to_hubspot(integration_id: int, *, db: Session | None = None) -> SyncResult:
    """Push new or updated leads to HubSpot."""
    return await _run_sync(
        integration_id=integration_id,
        direction="to_crm",
        handler=_push_hubspot,
        db=db,
    )


async def sync_from_hubspot(integration_id: int, *, db: Session | None = None) -> SyncResult:
    """Pull new or updated contacts from HubSpot."""
    return await _run_sync(
        integration_id=integration_id,
        direction="from_crm",
        handler=_pull_hubspot,
        db=db,
    )


async def resolve_conflicts(
    integration_id: int,
    decisions: List[Dict[str, Any]],
    *,
    db: Session | None = None,
) -> int:
    """Apply manual conflict resolutions based on user decisions."""
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        integration = (
            db.query(CRMIntegration)
            .filter(CRMIntegration.id == integration_id, CRMIntegration.active.is_(True))
            .one_or_none()
        )
        if not integration:
            raise ValueError(f"Active CRM integration {integration_id} not found.")

        applied = 0
        for decision in decisions:
            record_id = decision.get("record_id")
            preferred_source = decision.get("preferred_source")
            local_data = decision.get("local_data", {})
            remote_data = decision.get("remote_data", {})

            lead = db.query(Lead).filter(Lead.id == record_id).one_or_none()
            if not lead:
                logger.warning("Conflict resolution skipped, lead %s not found", record_id)
                continue

            if preferred_source == "remote":
                _apply_remote_payload_to_lead(lead, remote_data)
                calculate_lead_score(lead.id, db=db)
            else:
                # local preferred: nothing to change locally, but mark metadata for remote push
                metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
                crm_state = metadata.setdefault("crm_sync", {})
                provider_state = crm_state.setdefault(integration.provider, {})
                provider_state["needs_remote_update"] = True
                lead._metadata = metadata

            applied += 1

        db.commit()
        return applied
    finally:
        if owns_session:
            db.close()


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

async def _run_sync(
    integration_id: int,
    *,
    direction: str,
    handler,
    db: Session | None = None,
) -> SyncResult:
    """Generic sync execution wrapper handling logs and error propagation."""
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        integration = (
            db.query(CRMIntegration)
            .filter(CRMIntegration.id == integration_id, CRMIntegration.active.is_(True))
            .one_or_none()
        )
        if not integration:
            raise ValueError(f"Active CRM integration {integration_id} not found.")

        log = SyncLog(integration_id=integration.id, direction=direction)
        db.add(log)
        db.commit()
        db.refresh(log)

        try:
            records, errors = await handler(integration, log, db)
            status = "success" if not errors else "partial"
            log.mark_completed(records=records, status=status, errors=errors or None)
            integration.last_sync = datetime.utcnow()
            _update_integration_metadata(integration, status=status)
            db.add_all([integration, log])
            db.commit()
            return records, errors
        except Exception as exc:
            logger.exception("CRM sync failed for integration %s: %s", integration.id, exc)
            log.mark_completed(records=0, status="failed", errors=[{"message": str(exc)}])
            db.add(log)
            db.commit()
            raise
    finally:
        if owns_session:
            db.close()


async def _push_salesforce(integration: CRMIntegration, log: SyncLog, db: Session) -> SyncResult:
    client = _build_salesforce_client(integration)
    leads = _select_local_leads(db, integration)
    if not leads:
        return 0, []

    errors: List[Dict[str, Any]] = []
    processed = 0

    for lead in leads:
        payload = _map_lead_to_remote(lead, integration.field_mappings)
        try:
            await _upsert_salesforce_lead(client, payload)
        except CRMRateLimitError as exc:
            errors.append({"lead_id": str(lead.id), "message": str(exc), "type": "rate_limit"})
            break
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Salesforce push failed for lead %s", lead.id)
            errors.append({"lead_id": str(lead.id), "message": str(exc)})
            continue

        processed += 1
        _flag_lead_synced(lead, provider="salesforce", direction="to_crm")
        db.add(lead)

    db.commit()
    return processed, errors


async def _pull_salesforce(integration: CRMIntegration, log: SyncLog, db: Session) -> SyncResult:
    client = _build_salesforce_client(integration)
    records = await _fetch_salesforce_records(client, integration)

    errors: List[Dict[str, Any]] = []
    processed = 0

    for record in records:
        lead = _find_or_initialize_lead(db, record.get("Id"))
        try:
            _apply_remote_payload_to_lead(lead, record)
            calculate_lead_score(lead.id, db=db)
            _flag_lead_synced(lead, provider="salesforce", direction="from_crm")
            db.add(lead)
            processed += 1
        except Exception as exc:  # pragma: no cover - defensive
            logger.exception("Failed to ingest Salesforce record %s", record.get("Id"))
            errors.append({"record_id": record.get("Id"), "message": str(exc)})

    db.commit()
    return processed, errors


async def _push_hubspot(integration: CRMIntegration, log: SyncLog, db: Session) -> SyncResult:
    client = _build_hubspot_client(integration)
    leads = _select_local_leads(db, integration)
    if not leads:
        return 0, []

    errors: List[Dict[str, Any]] = []
    processed = 0

    for lead in leads:
        payload = _map_lead_to_remote(lead, integration.field_mappings)
        try:
            await _upsert_hubspot_contact(client, payload)
        except CRMRateLimitError as exc:
            errors.append({"lead_id": str(lead.id), "message": str(exc), "type": "rate_limit"})
            break
        except Exception as exc:  # pragma: no cover
            logger.exception("HubSpot push failed for lead %s", lead.id)
            errors.append({"lead_id": str(lead.id), "message": str(exc)})
            continue

        processed += 1
        _flag_lead_synced(lead, provider="hubspot", direction="to_crm")
        db.add(lead)

    db.commit()
    return processed, errors


async def _pull_hubspot(integration: CRMIntegration, log: SyncLog, db: Session) -> SyncResult:
    client = _build_hubspot_client(integration)
    records = await _fetch_hubspot_contacts(client, integration)

    errors: List[Dict[str, Any]] = []
    processed = 0

    for record in records:
        lead = _find_or_initialize_lead(db, record.get("id"))
        try:
            _apply_remote_payload_to_lead(lead, record)
            calculate_lead_score(lead.id, db=db)
            _flag_lead_synced(lead, provider="hubspot", direction="from_crm")
            db.add(lead)
            processed += 1
        except Exception as exc:  # pragma: no cover
            logger.exception("Failed to ingest HubSpot record %s", record.get("id"))
            errors.append({"record_id": record.get("id"), "message": str(exc)})

    db.commit()
    return processed, errors


def _select_local_leads(db: Session, integration: CRMIntegration) -> List[Lead]:
    query = db.query(Lead)
    if integration.last_sync:
        query = query.filter(Lead.updated_at > integration.last_sync)
    result = query.all()
    logger.info("Found %s local leads for integration %s", len(result), integration.id)
    return result


def _find_or_initialize_lead(db: Session, external_id: Optional[str]) -> Lead:
    if external_id:
        lead = (
            db.query(Lead)
            .filter(Lead._metadata["external_id"].astext == external_id)  # type: ignore[index]
            .one_or_none()
        )
        if lead:
            return lead

    lead = Lead(
        name="Imported Contact",
        email=f"unknown-{datetime.utcnow().timestamp()}@example.com",
        source="crm_import",
        metadata={},  # type: ignore[arg-type]
    )
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    if external_id:
        metadata["external_id"] = external_id
    lead._metadata = metadata
    db.add(lead)
    db.flush()
    return lead


def _map_lead_to_remote(lead: Lead, field_mappings: Dict[str, Any]) -> Dict[str, Any]:
    mapping = defaultdict(lambda: None)
    entries = field_mappings if isinstance(field_mappings, list) else field_mappings.get("fields", [])

    for entry in entries:
        local_key = entry.get("local_field")
        remote_key = entry.get("remote_field")
        if not local_key or not remote_key:
            continue
        value = getattr(lead, local_key, None)
        if value is None and isinstance(lead._metadata, dict):
            value = lead._metadata.get(local_key)
        mapping[remote_key] = value

    return dict(mapping)


def _apply_remote_payload_to_lead(lead: Lead, payload: Dict[str, Any]) -> None:
    # Basic mapping; in reality this would respect stored field mappings.
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    for key, value in payload.items():
        metadata[f"crm:{key}"] = value
    lead._metadata = metadata
    lead.updated_at = datetime.utcnow()


def _flag_lead_synced(lead: Lead, *, provider: str, direction: str) -> None:
    metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
    crm_state = metadata.setdefault("crm_sync", {})
    provider_state = crm_state.setdefault(provider, {})
    provider_state["last_sync"] = datetime.utcnow().isoformat()
    provider_state["last_direction"] = direction
    provider_state["status"] = "success"
    metadata["crm_sync"] = crm_state
    lead._metadata = metadata


def _update_integration_metadata(integration: CRMIntegration, *, status: str) -> None:
    # Placeholder for future stats aggregation.
    integration.updated_at = datetime.utcnow()


def _build_salesforce_client(integration: CRMIntegration) -> Salesforce:
    creds = integration.credentials
    try:
        return Salesforce(
            username=creds.get("username"),
            password=creds.get("password"),
            security_token=creds.get("security_token"),
            domain=creds.get("domain") or settings.salesforce_default_domain,
        )
    except Exception as exc:  # pragma: no cover - depends on real credentials
        raise CRMAuthError(f"Salesforce authentication failed: {exc}") from exc


def _build_hubspot_client(integration: CRMIntegration) -> HubSpot:
    creds = integration.credentials
    try:
        return HubSpot(access_token=creds.get("access_token"))
    except Exception as exc:  # pragma: no cover
        raise CRMAuthError(f"HubSpot authentication failed: {exc}") from exc


@retry(
    stop=stop_after_attempt(settings.crm_sync_max_retries),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type(CRMRateLimitError),
)
async def _upsert_salesforce_lead(client: Salesforce, payload: Dict[str, Any]) -> None:
    # Placeholder for real upsert call to Salesforce
    await asyncio.sleep(0)
    if not payload:
        raise ValueError("Payload is empty")


@retry(
    stop=stop_after_attempt(settings.crm_sync_max_retries),
    wait=wait_exponential(multiplier=1, min=1, max=30),
    retry=retry_if_exception_type(CRMRateLimitError),
)
async def _upsert_hubspot_contact(client: HubSpot, payload: Dict[str, Any]) -> None:
    # Placeholder for real HubSpot upsert call
    await asyncio.sleep(0)
    if not payload:
        raise ValueError("Payload is empty")


async def _fetch_salesforce_records(client: Salesforce, integration: CRMIntegration) -> List[Dict[str, Any]]:
    # Placeholder for Salesforce query - returns empty list to avoid real API dependency
    await asyncio.sleep(0)
    return []


async def _fetch_hubspot_contacts(client: HubSpot, integration: CRMIntegration) -> List[Dict[str, Any]]:
    await asyncio.sleep(0)
    return []

