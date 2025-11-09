"""Service layer exports."""

from .scoring_service import calculate_lead_score
from .auto_assignment import auto_assign_lead, test_rule_against_lead, apply_rule_to_lead
from .ai_insights import generate_lead_insights, generate_email_template, get_next_best_actions
from .email_sync import (
    sync_gmail_emails,
    sync_outlook_emails,
    sync_all_email_accounts,
    send_email_via_integration,
)
from .crm_sync import (
    sync_to_pipedrive,
    sync_from_pipedrive,
    resolve_conflicts,
)

__all__ = [
    "calculate_lead_score",
    "auto_assign_lead",
    "test_rule_against_lead",
    "apply_rule_to_lead",
    "generate_lead_insights",
    "generate_email_template",
    "get_next_best_actions",
    "sync_gmail_emails",
    "sync_outlook_emails",
    "sync_all_email_accounts",
    "send_email_via_integration",
    "sync_to_pipedrive",
    "sync_from_pipedrive",
    "resolve_conflicts",
]
