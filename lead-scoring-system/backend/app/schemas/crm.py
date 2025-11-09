"""Schemas for CRM (Salesforce/HubSpot) integrations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field

CRMProvider = Literal["salesforce", "hubspot"]
SyncDirection = Literal["to_crm", "from_crm", "bidirectional"]
SyncFrequency = Literal["manual", "hourly", "daily"]
ConflictStrategy = Literal["manual", "prefer_crm", "prefer_local"]
SyncStatus = Literal["running", "success", "partial", "failed"]


class FieldMappingEntry(BaseModel):
    local_field: str
    remote_field: str
    transform: Optional[str] = Field(
        default=None,
        description="Optional transform hint applied before syncing (e.g. 'lowercase', 'format_phone').",
    )


class CRMIntegrationBase(BaseModel):
    sync_direction: SyncDirection = "bidirectional"
    sync_frequency: SyncFrequency = "manual"
    field_mappings: List[FieldMappingEntry] = Field(default_factory=list)
    conflict_strategy: ConflictStrategy = "manual"


class SalesforceCredentials(BaseModel):
    username: str
    password: str
    security_token: str
    domain: Optional[str] = None


class HubSpotCredentials(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    app_id: Optional[str] = None


class SalesforceConnectRequest(CRMIntegrationBase):
    credentials: SalesforceCredentials


class HubSpotConnectRequest(CRMIntegrationBase):
    credentials: HubSpotCredentials


class CRMIntegrationRead(CRMIntegrationBase):
    id: int
    provider: CRMProvider
    last_sync: Optional[datetime] = None
    active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CRMSyncTriggerRequest(BaseModel):
    direction: Optional[SyncDirection] = None
    force_full_sync: bool = False


class SyncLogRead(BaseModel):
    id: int
    integration_id: int
    sync_started: datetime
    sync_completed: Optional[datetime]
    records_synced: int
    errors: Optional[List[Dict[str, Any]]]
    status: SyncStatus
    direction: SyncDirection
    provider: CRMProvider

    class Config:
        from_attributes = True


class SyncStatusResponse(BaseModel):
    integration: Optional[CRMIntegrationRead]
    latest_log: Optional[SyncLogRead]


class ConflictRecord(BaseModel):
    record_id: str
    local_data: Dict[str, Any]
    remote_data: Dict[str, Any]
    preferred_source: Literal["local", "remote"]


class ConflictResolutionRequest(BaseModel):
    conflicts: List[ConflictRecord]

