"""Schemas for lead import/export operations."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ImportErrorDetail(BaseModel):
    row_number: int
    email: Optional[str] = None
    message: str


class LeadImportSummary(BaseModel):
    total_rows: int
    success_count: int
    error_count: int
    errors: List[ImportErrorDetail] = Field(default_factory=list)
    preview: List[Dict[str, Any]] = Field(default_factory=list)
    error_report: Optional[str] = None  # base64-encoded CSV of errors


class LeadExportFilters(BaseModel):
    classification: Optional[str] = None
    status: Optional[str] = None
    source: Optional[str] = None
    created_from: Optional[datetime] = None
    created_to: Optional[datetime] = None
    assigned_to: Optional[UUID] = None


class LeadExportRequest(BaseModel):
    filters: LeadExportFilters = Field(default_factory=LeadExportFilters)
    include_fields: List[str] = Field(
        default_factory=lambda: ["basic", "contact", "score"]
    )
    file_name: Optional[str] = None


class LeadImportResponse(LeadImportSummary):
    """Alias for backwards compatibility."""


