"""Pydantic schemas for score-related responses."""

from typing import Dict

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    engagement: int = Field(..., ge=0, le=40)
    buying_signals: int = Field(..., ge=0, le=40)
    demographic_fit: int = Field(..., ge=0, le=20)


class ScoreResponse(BaseModel):
    total_score: int = Field(..., ge=0, le=100)
    classification: str
    breakdown: ScoreBreakdown
    details: Dict[str, int] = Field(default_factory=dict)
