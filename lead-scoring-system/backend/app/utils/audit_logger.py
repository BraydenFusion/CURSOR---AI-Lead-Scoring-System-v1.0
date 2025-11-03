"""Audit logging utility for tracking data modifications."""

import logging
from datetime import datetime
from typing import Optional
from uuid import UUID

logger = logging.getLogger("audit")


def log_data_modification(
    action: str,
    entity_type: str,
    entity_id: UUID,
    user_id: UUID,
    details: Optional[dict] = None,
) -> None:
    """
    Log data modification for audit trail.
    
    Args:
        action: Action performed (CREATE, UPDATE, DELETE)
        entity_type: Type of entity (lead, note, assignment, etc.)
        entity_id: ID of the entity
        user_id: ID of user performing the action
        details: Additional details about the modification
    """
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "entity_type": entity_type,
        "entity_id": str(entity_id),
        "user_id": str(user_id),
        "details": details or {},
    }
    
    logger.info(f"AUDIT: {action} {entity_type} {entity_id} by user {user_id}", extra=audit_entry)


def log_login_attempt(username: str, success: bool, ip_address: Optional[str] = None) -> None:
    """Log login attempts for security auditing."""
    logger.info(
        f"LOGIN: {'SUCCESS' if success else 'FAILED'} - username: {username}, ip: {ip_address or 'unknown'}"
    )


def log_permission_denied(user_id: UUID, resource: str, action: str) -> None:
    """Log permission denied attempts."""
    logger.warning(
        f"PERMISSION_DENIED: user {user_id} attempted {action} on {resource}"
    )

