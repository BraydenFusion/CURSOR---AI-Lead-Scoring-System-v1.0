"""Schemas for AI insights and email assistance endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import List, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class ActionItem(BaseModel):
    title: str
    description: str
    priority: int = Field(default=3, ge=1, le=5)
    time_estimate: str = Field(default="30 minutes")
    done: bool = Field(default=False)


class ConversionProbability(BaseModel):
    level: Literal["low", "medium", "high", "unknown"]
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    reasoning: List[str] = Field(default_factory=list)
    comparison_to_similar: Optional[str] = None

    @field_validator("level", mode="before")
    @classmethod
    def normalize_level(cls, value: str) -> str:
        if not value:
            return "unknown"
        value = value.lower()
        if value not in {"low", "medium", "high", "unknown"}:
            return "unknown"
        return value


class TalkingPoint(BaseModel):
    title: str
    details: str


class AIInsightResponse(BaseModel):
    lead_id: UUID
    summary: str
    summary_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    recommended_actions: List[ActionItem]
    conversion_probability: ConversionProbability
    talking_points: List[TalkingPoint]
    generated_at: datetime
    estimated_cost: Optional[float] = Field(default=None, ge=0.0)


class EmailTemplateRequest(BaseModel):
    lead_id: UUID
    email_type: Literal["initial_outreach", "follow_up", "demo_invite", "pricing_discussion"]


class EmailTemplateResponse(BaseModel):
    subject: str
    body: str
    call_to_action: Optional[str] = None
    generated_at: datetime
    estimated_cost: Optional[float] = Field(default=None, ge=0.0)


class NextBestActionResponse(BaseModel):
    lead_id: UUID
    recommended_actions: List[ActionItem]
    generated_at: datetime

