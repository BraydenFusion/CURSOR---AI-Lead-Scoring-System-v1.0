"""Pydantic schemas for saved reports."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

ALLOWED_REPORT_TYPES = {"conversion", "source_analysis", "rep_performance", "custom"}
ALLOWED_SCHEDULES = {"manual", "daily", "weekly", "monthly"}


class ReportBase(BaseModel):
    """Base fields for report definitions."""

    name: str = Field(..., max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    report_type: str = Field(default="custom")
    filters: Dict[str, Any] = Field(default_factory=dict)
    metrics: List[str] = Field(default_factory=list)
    schedule: Optional[str] = Field(
        default=None,
        description="Report schedule: manual, daily, weekly, monthly",
    )

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, value: str) -> str:
        report_type = value.lower()
        if report_type not in ALLOWED_REPORT_TYPES:
            raise ValueError(f"Invalid report_type '{value}'. Must be one of {sorted(ALLOWED_REPORT_TYPES)}")
        return report_type

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        schedule_value = value.lower()
        if schedule_value not in ALLOWED_SCHEDULES:
            raise ValueError(f"Invalid schedule '{value}'. Must be one of {sorted(ALLOWED_SCHEDULES)}")
        return schedule_value


class ReportCreate(ReportBase):
    """Payload for creating a new report."""

    metrics: List[str] = Field(..., min_length=1, description="At least one metric must be selected.")


class ReportUpdate(BaseModel):
    """Payload for updating an existing report."""

    name: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    report_type: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None
    metrics: Optional[List[str]] = None
    schedule: Optional[str] = None

    @field_validator("report_type")
    @classmethod
    def validate_report_type(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        report_type = value.lower()
        if report_type not in ALLOWED_REPORT_TYPES:
            raise ValueError(f"Invalid report_type '{value}'. Must be one of {sorted(ALLOWED_REPORT_TYPES)}")
        return report_type

    @field_validator("schedule")
    @classmethod
    def validate_schedule(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        schedule_value = value.lower()
        if schedule_value not in ALLOWED_SCHEDULES:
            raise ValueError(f"Invalid schedule '{value}'. Must be one of {sorted(ALLOWED_SCHEDULES)}")
        return schedule_value


class ReportResponse(ReportBase):
    """Response payload for saved reports."""

    id: int
    created_at: datetime
    last_run: Optional[datetime]

    class Config:
        from_attributes = True


class ReportRunRequest(BaseModel):
    """Optional payload to override filters when running a report."""

    filters: Optional[Dict[str, Any]] = None


class ReportRunResult(BaseModel):
    """Result payload for running a report."""

    report_id: int
    generated_at: datetime
    metrics: List[str]
    data: Dict[str, Any]


