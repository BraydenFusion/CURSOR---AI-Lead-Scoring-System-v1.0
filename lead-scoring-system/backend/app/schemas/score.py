"""Pydantic schemas for score-related responses."""

from typing import List, Union

from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    engagement: int = Field(..., ge=0, le=40)
    buying_signals: int = Field(..., ge=0, le=40)
    demographic_fit: int = Field(..., ge=0, le=20)


class ScoreFactor(BaseModel):
    name: str
    value: Union[str, int, float]
    points: int
    max_points: int


class ScoreDetails(BaseModel):
    engagement_factors: List[ScoreFactor]
    buying_factors: List[ScoreFactor]
    demographic_factors: List[ScoreFactor]


class ScoreResponse(BaseModel):
    total_score: int = Field(..., ge=0, le=100)
    classification: str
    breakdown: ScoreBreakdown
    details: ScoreDetails
