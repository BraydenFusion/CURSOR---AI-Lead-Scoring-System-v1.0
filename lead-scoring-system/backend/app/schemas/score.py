"""Pydantic schemas for score-related responses."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

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


# New schemas for PRD AI scoring system
class InsightResponse(BaseModel):
    """Schema for AI-generated insight."""
    type: str  # 'talking_point', 'concern', 'opportunity'
    content: str
    confidence: float = Field(..., ge=0.0, le=1.0)


class AIScoreResponse(BaseModel):
    """Enhanced AI score response per PRD."""
    lead_id: UUID
    overall_score: int = Field(..., ge=0, le=100)
    engagement_score: int = Field(..., ge=0, le=100)
    buying_signal_score: int = Field(..., ge=0, le=100)
    demographic_score: int = Field(..., ge=0, le=100)
    priority_tier: str  # 'HOT', 'WARM', 'COLD'
    confidence_level: float = Field(..., ge=0.0, le=1.0)
    scored_at: datetime
    insights: List[InsightResponse] = Field(default_factory=list)
    scoring_metadata: Optional[Dict] = None


class PrioritizedLeadItem(BaseModel):
    """Schema for prioritized lead in top 5 list."""
    id: UUID
    name: str
    email: str
    phone: Optional[str] = None
    score: int = Field(..., ge=0, le=100)
    priority_tier: str
    vehicle_interest: Optional[str] = None
    budget_range: Optional[str] = None
    time_since_inquiry: str
    insights: List[InsightResponse] = Field(default_factory=list)
    suggested_actions: List[str] = Field(default_factory=list)


class PrioritizedLeadsResponse(BaseModel):
    """Response for prioritized leads endpoint."""
    leads: List[PrioritizedLeadItem]
    total_hot: int
    total_warm: int
    total_cold: int


class ScoreDistribution(BaseModel):
    """Score distribution buckets."""
    range_80_100: int = Field(alias="80-100", default=0)
    range_60_79: int = Field(alias="60-79", default=0)
    range_40_59: int = Field(alias="40-59", default=0)
    range_0_39: int = Field(alias="0-39", default=0)


class ScoringAnalyticsResponse(BaseModel):
    """Analytics response for scoring metrics."""
    score_distribution: Dict[str, int]
    avg_response_time_by_tier: Dict[str, str]
    conversion_rate_by_tier: Optional[Dict[str, float]] = None
