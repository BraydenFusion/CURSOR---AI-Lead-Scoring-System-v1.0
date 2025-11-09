"""API routes for Salesforce and HubSpot CRM integrations."""

from __future__ import annotations

import asyncio
from typing import List, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import SessionLocal, get_db
from app.models import CRMIntegration, SyncLog, UserRole
from app.schemas import (
    CRMIntegrationRead,
    SalesforceConnectRequest,
    HubSpotConnectRequest,
    CRMSyncTriggerRequest,
    SyncLogRead,
    SyncStatusResponse,
    ConflictResolutionRequest,
)
from app.services.crm_sync import (
    resolve_conflicts,
    sync_from_hubspot,
    sync_from_salesforce,
    sync_to_hubspot,
    sync_to_salesforce,
)
from app.utils.auth import get_current_active_user, require_role

router = APIRouter()


def _serialize_integration(integration: CRMIntegration) -> CRMIntegrationRead:
    return CRMIntegrationRead(
        id=integration.id,
        provider=integration.provider,  # type: ignore[arg-type]
        sync_direction=integration.sync_direction,  # type: ignore[arg-type]
        sync_frequency=integration.sync_frequency,  # type: ignore[arg-type]
        field_mappings=integration.field_mappings.get("fields", []) if isinstance(integration.field_mappings, dict) else integration.field_mappings,  # type: ignore[arg-type]
        conflict_strategy=integration.conflict_strategy,  # type: ignore[arg-type]
        last_sync=integration.last_sync,
        active=integration.active,
        created_at=integration.created_at,
        updated_at=integration.updated_at,
    )


def _serialize_log(log: SyncLog) -> SyncLogRead:
    return SyncLogRead(
        id=log.id,
        integration_id=log.integration_id,
        sync_started=log.sync_started,
        sync_completed=log.sync_completed,
        records_synced=log.records_synced,
        errors=log.errors,
        status=log.status,  # type: ignore[arg-type]
        direction=log.direction,  # type: ignore[arg-type]
        provider=log.integration.provider,  # type: ignore[arg-type]
    )


@router.get(
    "/integrations",
    response_model=List[CRMIntegrationRead],
    dependencies=[Depends(get_current_active_user)],
)
def list_crm_integrations(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> List[CRMIntegrationRead]:
    integrations = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id)
        .order_by(CRMIntegration.provider.asc())
        .all()
    )
    return [_serialize_integration(integration) for integration in integrations]


@router.post(
    "/salesforce/connect",
    response_model=CRMIntegrationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
def connect_salesforce(
    payload: SalesforceConnectRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> CRMIntegrationRead:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id, CRMIntegration.provider == "salesforce")
        .one_or_none()
    )
    field_payload = {"fields": [entry.dict() for entry in payload.field_mappings]}

    if integration:
        integration.credentials = payload.credentials.dict()
        integration.sync_direction = payload.sync_direction
        integration.sync_frequency = payload.sync_frequency
        integration.field_mappings = field_payload
        integration.conflict_strategy = payload.conflict_strategy
        integration.active = True
    else:
        integration = CRMIntegration(
            user_id=current_user.id,
            provider="salesforce",
            sync_direction=payload.sync_direction,
            sync_frequency=payload.sync_frequency,
            field_mappings=field_payload,
            conflict_strategy=payload.conflict_strategy,
        )
        integration.credentials = payload.credentials.dict()
        db.add(integration)

    db.commit()
    db.refresh(integration)
    return _serialize_integration(integration)


@router.post(
    "/hubspot/connect",
    response_model=CRMIntegrationRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
def connect_hubspot(
    payload: HubSpotConnectRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> CRMIntegrationRead:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id, CRMIntegration.provider == "hubspot")
        .one_or_none()
    )
    field_payload = {"fields": [entry.dict() for entry in payload.field_mappings]}

    if integration:
        integration.credentials = payload.credentials.dict()
        integration.sync_direction = payload.sync_direction
        integration.sync_frequency = payload.sync_frequency
        integration.field_mappings = field_payload
        integration.conflict_strategy = payload.conflict_strategy
        integration.active = True
    else:
        integration = CRMIntegration(
            user_id=current_user.id,
            provider="hubspot",
            sync_direction=payload.sync_direction,
            sync_frequency=payload.sync_frequency,
            field_mappings=field_payload,
            conflict_strategy=payload.conflict_strategy,
        )
        integration.credentials = payload.credentials.dict()
        db.add(integration)

    db.commit()
    db.refresh(integration)
    return _serialize_integration(integration)


@router.patch(
    "/integrations/{integration_id}",
    response_model=CRMIntegrationRead,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
def update_integration(
    integration_id: int,
    payload: CRMSyncTriggerRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> CRMIntegrationRead:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.id == integration_id, CRMIntegration.user_id == current_user.id)
        .one_or_none()
    )
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found.")

    if payload.direction:
        integration.sync_direction = payload.direction
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return _serialize_integration(integration)


@router.get(
    "/salesforce/status",
    response_model=SyncStatusResponse,
    dependencies=[Depends(get_current_active_user)],
)
def salesforce_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SyncStatusResponse:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id, CRMIntegration.provider == "salesforce")
        .one_or_none()
    )
    if not integration:
        return SyncStatusResponse(integration=None, latest_log=None)

    log = (
        db.query(SyncLog)
        .filter(SyncLog.integration_id == integration.id)
        .order_by(SyncLog.sync_started.desc())
        .first()
    )
    return SyncStatusResponse(
        integration=_serialize_integration(integration),
        latest_log=_serialize_log(log) if log else None,
    )


@router.get(
    "/hubspot/status",
    response_model=SyncStatusResponse,
    dependencies=[Depends(get_current_active_user)],
)
def hubspot_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SyncStatusResponse:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id, CRMIntegration.provider == "hubspot")
        .one_or_none()
    )
    if not integration:
        return SyncStatusResponse(integration=None, latest_log=None)

    log = (
        db.query(SyncLog)
        .filter(SyncLog.integration_id == integration.id)
        .order_by(SyncLog.sync_started.desc())
        .first()
    )
    return SyncStatusResponse(
        integration=_serialize_integration(integration),
        latest_log=_serialize_log(log) if log else None,
    )


@router.post(
    "/salesforce/sync",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
async def trigger_salesforce_sync(
    payload: CRMSyncTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SyncStatusResponse:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id, CRMIntegration.provider == "salesforce")
        .one_or_none()
    )
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Salesforce integration not found.")

    direction = payload.direction or integration.sync_direction

    async def _sync() -> None:
        async with _session_scope() as session:
            if direction in ("to_crm", "bidirectional"):
                await sync_to_salesforce(integration.id, db=session)
            if direction in ("from_crm", "bidirectional"):
                await sync_from_salesforce(integration.id, db=session)

    background_tasks.add_task(asyncio.create_task, _sync())
    return salesforce_status(db=db, current_user=current_user)


@router.post(
    "/hubspot/sync",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
async def trigger_hubspot_sync(
    payload: CRMSyncTriggerRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> SyncStatusResponse:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.user_id == current_user.id, CRMIntegration.provider == "hubspot")
        .one_or_none()
    )
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HubSpot integration not found.")

    direction = payload.direction or integration.sync_direction

    async def _sync() -> None:
        async with _session_scope() as session:
            if direction in ("to_crm", "bidirectional"):
                await sync_to_hubspot(integration.id, db=session)
            if direction in ("from_crm", "bidirectional"):
                await sync_from_hubspot(integration.id, db=session)

    background_tasks.add_task(asyncio.create_task, _sync())
    return hubspot_status(db=db, current_user=current_user)


@router.get(
    "/sync-logs",
    response_model=List[SyncLogRead],
    dependencies=[Depends(get_current_active_user)],
)
def list_sync_logs(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> List[SyncLogRead]:
    logs = (
        db.query(SyncLog)
        .join(CRMIntegration, CRMIntegration.id == SyncLog.integration_id)
        .filter(CRMIntegration.user_id == current_user.id)
        .order_by(SyncLog.sync_started.desc())
        .limit(limit)
        .all()
    )
    return [_serialize_log(log) for log in logs]


@router.post(
    "/integrations/{integration_id}/resolve-conflicts",
    status_code=status.HTTP_202_ACCEPTED,
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
async def resolve_sync_conflicts(
    integration_id: int,
    payload: ConflictResolutionRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_active_user),
) -> dict:
    integration = (
        db.query(CRMIntegration)
        .filter(CRMIntegration.id == integration_id, CRMIntegration.user_id == current_user.id)
        .one_or_none()
    )
    if not integration:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Integration not found.")

    applied = await resolve_conflicts(integration_id, [conflict.dict() for conflict in payload.conflicts], db=db)
    return {"applied": applied}


class _session_scope:
    """Async context manager to provide a database session inside background tasks."""

    def __init__(self) -> None:
        self.session: Optional[Session] = None

    async def __aenter__(self) -> Session:
        self.session = SessionLocal()
        return self.session

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self.session is None:
            return
        if exc:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()

