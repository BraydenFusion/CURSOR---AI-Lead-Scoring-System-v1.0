"""SQLAlchemy models for the lead scoring system."""

from .lead import Lead, LeadStatus
from .activity import LeadActivity
from .score_history import LeadScoreHistory
from .user import User, UserRole
from .assignment import LeadAssignment
from .note import LeadNote
from .notification import Notification, NotificationType
from .ai_scoring import LeadScore, LeadEngagementEvent, LeadInsight
from .report import SavedReport
from .assignment_rule import AssignmentRule
from .email_integration import EmailAccount, EmailMessage
from .crm_integration import CRMIntegration, SyncLog

__all__ = [
    "Lead",
    "LeadStatus",
    "LeadActivity",
    "LeadScoreHistory",
    "User",
    "UserRole",
    "LeadAssignment",
    "LeadNote",
    "Notification",
    "NotificationType",
    "LeadScore",
    "LeadEngagementEvent",
    "LeadInsight",
    "SavedReport",
    "AssignmentRule",
    "EmailAccount",
    "EmailMessage",
    "CRMIntegration",
    "SyncLog",
]
