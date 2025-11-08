"""Schemas for assignment rule management."""

from __future__ import annotations

from datetime import datetime
from typing import Annotated, Any, Dict, List, Literal, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, model_validator


class AssignmentRuleConditions(BaseModel):
    lead_score_min: Optional[int] = Field(default=None, ge=0, le=100)
    lead_score_max: Optional[int] = Field(default=None, ge=0, le=100)
    sources: List[str] = Field(default_factory=list)
    locations: List[str] = Field(default_factory=list)
    days_of_week: List[int] = Field(default_factory=list, description="ISO weekday numbers 1 (Mon) - 7 (Sun)")
    business_hours_only: bool = False
    metadata_contains: Dict[str, Any] = Field(default_factory=dict)

    @field_validator("days_of_week", mode="before")
    @classmethod
    def _validate_days(cls, value: Any) -> List[int]:
        if value is None:
            return []
        if isinstance(value, int):
            value = [value]
        if not isinstance(value, list):
            raise ValueError("days_of_week must be a list of integers between 1 and 7")
        unique_days: List[int] = []
        for item in value:
            try:
                day = int(item)
            except (TypeError, ValueError) as exc:
                raise ValueError("days_of_week must be integers between 1 and 7") from exc
            if day < 1 or day > 7:
                raise ValueError("days_of_week entries must be between 1 and 7")
            if day not in unique_days:
                unique_days.append(day)
        return unique_days

    @model_validator(mode="after")
    def _validate_score_range(self) -> "AssignmentRuleConditions":
        if (
            self.lead_score_min is not None
            and self.lead_score_max is not None
            and self.lead_score_min > self.lead_score_max
        ):
            raise ValueError("lead_score_min must be less than or equal to lead_score_max")
        return self


class RoundRobinLogic(BaseModel):
    type: Literal["round_robin"]
    eligible_reps: List[UUID] = Field(min_length=1)
    max_leads_per_rep: Optional[int] = Field(default=None, ge=1)


class TerritoryLogic(BaseModel):
    type: Literal["territory"]
    territory_mapping: Dict[str, List[UUID]] = Field(default_factory=dict)
    eligible_reps: Optional[List[UUID]] = None
    max_leads_per_rep: Optional[int] = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _validate_mapping(self) -> "TerritoryLogic":
        for territory, reps in self.territory_mapping.items():
            if not reps:
                raise ValueError(f"Territory '{territory}' must have at least one representative")
        return self


class WorkloadLogic(BaseModel):
    type: Literal["workload"]
    eligible_reps: Optional[List[UUID]] = None
    max_leads_per_rep: Optional[int] = Field(default=None, ge=1)


class ScoreTier(BaseModel):
    min_score: int = Field(ge=0, le=100)
    max_score: int = Field(ge=0, le=100)
    reps: List[UUID] = Field(min_length=1)
    max_leads_per_rep: Optional[int] = Field(default=None, ge=1)

    @model_validator(mode="after")
    def _validate_range(self) -> "ScoreTier":
        if self.min_score > self.max_score:
            raise ValueError("Tier min_score must be less than or equal to max_score")
        return self


class ScoreBasedLogic(BaseModel):
    type: Literal["score_based"]
    tiers: List[ScoreTier] = Field(min_length=1)
    fallback_reps: Optional[List[UUID]] = None
    max_leads_per_rep: Optional[int] = Field(default=None, ge=1)


AssignmentLogicUnion = Annotated[
    Union[RoundRobinLogic, TerritoryLogic, WorkloadLogic, ScoreBasedLogic],
    Field(discriminator="type"),
]


class AssignmentRuleBase(BaseModel):
    name: str = Field(..., max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: int = Field(default=5, ge=1, le=10)
    rule_type: Literal["round_robin", "territory", "workload", "score_based"]
    conditions: AssignmentRuleConditions = Field(default_factory=AssignmentRuleConditions)
    assignment_logic: AssignmentLogicUnion

    @model_validator(mode="after")
    def _ensure_matching_rule_type(self) -> "AssignmentRuleBase":
        if self.rule_type != self.assignment_logic.type:
            raise ValueError("rule_type must match assignment_logic.type")
        return self


class AssignmentRuleCreate(AssignmentRuleBase):
    active: bool = Field(default=True)


class AssignmentRuleUpdate(BaseModel):
    name: Optional[str] = Field(default=None, max_length=150)
    description: Optional[str] = Field(default=None, max_length=500)
    priority: Optional[int] = Field(default=None, ge=1, le=10)
    active: Optional[bool] = None
    rule_type: Optional[Literal["round_robin", "territory", "workload", "score_based"]] = None
    conditions: Optional[AssignmentRuleConditions] = None
    assignment_logic: Optional[AssignmentLogicUnion] = None

    @model_validator(mode="after")
    def _validate_rule_alignment(self) -> "AssignmentRuleUpdate":
        if self.rule_type and self.assignment_logic and self.rule_type != self.assignment_logic.type:
            raise ValueError("rule_type must match assignment_logic.type")
        return self


class AssignmentRuleRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    active: bool
    priority: int
    rule_type: str
    conditions: Dict[str, Any]
    assignment_logic: Dict[str, Any]
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AssignmentRuleToggleRequest(BaseModel):
    active: bool


class AssignmentRuleTestResponse(BaseModel):
    matches: bool
    rule_id: Optional[int] = None
    lead_id: Optional[str] = None
    assigned_user_id: Optional[str] = None
    assigned_user_name: Optional[str] = None
    reason: Optional[str] = None


class AssignmentEligibleRep(BaseModel):
    id: UUID
    full_name: str
    email: str
    active_assignments: int = 0


class AssignmentRuleApplyRequest(BaseModel):
    lead_id: UUID


class AssignmentRuleApplyResponse(BaseModel):
    success: bool
    assigned_user_id: Optional[str] = None
    assigned_user_name: Optional[str] = None
    message: Optional[str] = None

