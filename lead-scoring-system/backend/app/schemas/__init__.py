"""Pydantic schema exports for external usage."""

from .lead import LeadCreate, LeadRead, LeadListResponse, LeadUpdate, LeadStatusUpdate
from .activity import ActivityCreate, ActivityRead
from .score import ScoreBreakdown, ScoreResponse
from .user import UserCreate, UserLogin, UserResponse, Token, TokenData
from .assignment import AssignmentCreate, AssignmentResponse, AssignmentWithDetails
from .note import NoteCreate, NoteResponse, NotificationResponse

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
]
