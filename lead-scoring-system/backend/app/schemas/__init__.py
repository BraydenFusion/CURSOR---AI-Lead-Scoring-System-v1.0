"""Pydantic schema exports for external usage."""

from .lead import LeadCreate, LeadRead, LeadListResponse, LeadUpdate, LeadStatusUpdate
from .activity import ActivityCreate, ActivityRead
from .score import (
    ScoreBreakdown,
    ScoreResponse,
    AIScoreResponse,
    InsightResponse,
    PrioritizedLeadItem,
    PrioritizedLeadsResponse,
    ScoringAnalyticsResponse,
)
from .user import UserCreate, UserLogin, UserResponse, Token, TokenData
from .assignment import AssignmentCreate, AssignmentResponse, AssignmentWithDetails
from .assignment_rule import (
    AssignmentRuleCreate,
    AssignmentRuleRead,
    AssignmentRuleUpdate,
    AssignmentRuleConditions,
    AssignmentRuleToggleRequest,
    AssignmentRuleTestResponse,
    AssignmentEligibleRep,
    AssignmentRuleApplyRequest,
    AssignmentRuleApplyResponse,
)
from .note import NoteCreate, NoteResponse, NotificationResponse
from .ai import (
    AIInsightResponse,
    EmailTemplateRequest,
    EmailTemplateResponse,
    NextBestActionResponse,
    ActionItem,
    ConversionProbability,
    TalkingPoint,
)

__all__ = [
    "LeadCreate",
    "LeadRead",
    "LeadUpdate",
    "LeadStatusUpdate",
    "LeadListResponse",
    "ActivityCreate",
    "ActivityRead",
    "ScoreBreakdown",
    "ScoreResponse",
    "AIScoreResponse",
    "InsightResponse",
    "PrioritizedLeadItem",
    "PrioritizedLeadsResponse",
    "ScoringAnalyticsResponse",
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "Token",
    "TokenData",
    "AssignmentCreate",
    "AssignmentResponse",
    "AssignmentWithDetails",
    "NoteCreate",
    "NoteResponse",
    "NotificationResponse",
    "AssignmentRuleCreate",
    "AssignmentRuleRead",
    "AssignmentRuleUpdate",
    "AssignmentRuleConditions",
    "AssignmentRuleToggleRequest",
    "AssignmentRuleTestResponse",
    "AssignmentEligibleRep",
    "AssignmentRuleApplyRequest",
    "AssignmentRuleApplyResponse",
    "AIInsightResponse",
    "EmailTemplateRequest",
    "EmailTemplateResponse",
    "NextBestActionResponse",
    "ActionItem",
    "ConversionProbability",
    "TalkingPoint",
]
