"""Automated lead assignment service."""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import AssignmentRule, Lead, LeadAssignment, User, UserRole
from app.services.notification_service import notification_service

logger = logging.getLogger(__name__)

BUSINESS_HOURS_START = 8  # 8 AM UTC by default
BUSINESS_HOURS_END = 18  # 6 PM UTC


def auto_assign_lead(lead_id: UUID, *, db: Session | None = None) -> Optional[UUID]:
    """
    Automatically assign a lead based on active rules.

    Returns the assigned user's ID or None if no rules matched.
    """
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        lead: Lead | None = db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if lead is None:
            logger.warning("Lead %s not found for auto-assignment", lead_id)
            return None

        if _has_active_assignment(db, lead_id):
            logger.info("Lead %s already has an active assignment. Skipping auto-assignment.", lead_id)
            return None

        rules: List[AssignmentRule] = (
            db.query(AssignmentRule)
            .filter(AssignmentRule.active.is_(True))
            .order_by(AssignmentRule.priority.desc(), AssignmentRule.created_at.asc())
            .all()
        )

        now = datetime.utcnow()

        for rule in rules:
            if not rule or not _rule_matches_conditions(rule.conditions, lead, now):
                continue

            assignee_id = _resolve_assignment(db, rule, lead, now)
            if assignee_id is None:
                continue

            # Persist assignment
            assignment = LeadAssignment(
                lead_id=lead.id,
                user_id=assignee_id,
                assigned_by=None,
                notes=f"Auto-assigned via rule: {rule.name}",
                is_primary=True,
            )
            db.add(assignment)

            # Update rule state if modified
            db.add(rule)

            db.flush()

            assigned_user = db.query(User).filter(User.id == assignee_id).one_or_none()
            if assigned_user is None:
                logger.warning("Assigned user %s no longer exists. Rolling back assignment.", assignee_id)
                db.rollback()
                continue

            db.commit()

            try:
                notification_service.notify_lead_assigned(db, assigned_user, lead, send_email=True)
            except Exception:  # pragma: no cover - notification errors shouldn't block assignment
                logger.exception("Failed to send notification for auto-assignment lead %s", lead.id)

            logger.info(
                "Lead %s auto-assigned to user %s using rule %s (%s)",
                lead_id,
                assignee_id,
                rule.id,
                rule.rule_type,
            )

            return assignee_id

        logger.info("No matching assignment rules for lead %s", lead_id)
        return None
    except Exception:
        db.rollback()
        logger.exception("Error auto-assigning lead %s", lead_id)
        return None
    finally:
        if owns_session:
            db.close()


def _has_active_assignment(db: Session, lead_id: UUID) -> bool:
    return (
        db.query(LeadAssignment)
        .filter(LeadAssignment.lead_id == lead_id, LeadAssignment.status == "active")
        .count()
        > 0
    )


def _rule_matches_conditions(conditions: Dict[str, Any] | None, lead: Lead, now: datetime) -> bool:
    if not conditions:
        return True

    score_min = conditions.get("lead_score_min")
    score_max = conditions.get("lead_score_max")
    lead_score = lead.current_score or 0

    if score_min is not None and lead_score < score_min:
        return False
    if score_max is not None and lead_score > score_max:
        return False

    sources: List[str] | None = conditions.get("sources")
    if sources and lead.source not in sources:
        return False

    locations: List[str] | None = conditions.get("locations")
    lead_location = (lead.location or "").strip().lower()
    if locations:
        normalized = {loc.strip().lower() for loc in locations}
        if lead_location not in normalized:
            return False

    days_of_week: List[int] | None = conditions.get("days_of_week")
    if days_of_week:
        weekday = now.isoweekday()
        if weekday not in days_of_week:
            return False

    if conditions.get("business_hours_only"):
        if not BUSINESS_HOURS_START <= now.hour < BUSINESS_HOURS_END:
            return False

    metadata_filters: Dict[str, Any] | None = conditions.get("metadata_contains")
    if metadata_filters:
        lead_metadata = lead._metadata if isinstance(lead._metadata, dict) else {}
        for key, expected in metadata_filters.items():
            value = lead_metadata.get(key)
            if isinstance(expected, list):
                if value not in expected:
                    return False
            elif value != expected:
                return False

    return True


def _resolve_assignment(
    db: Session,
    rule: AssignmentRule,
    lead: Lead,
    now: datetime,
    *,
    dry_run: bool = False,
) -> Optional[UUID]:
    logic = rule.assignment_logic or {}
    rule_type = (rule.rule_type or logic.get("type") or "").lower()

    if rule_type == "round_robin":
        return _assign_round_robin(db, rule, logic, dry_run=dry_run)
    if rule_type == "territory":
        return _assign_by_territory(db, rule, logic, lead)
    if rule_type == "workload":
        return _assign_by_workload(db, rule, logic)
    if rule_type == "score_based":
        return _assign_by_score(db, rule, logic, lead)

    logger.warning("Unknown assignment rule type '%s' for rule %s", rule_type, rule.id)
    return None


def _assign_round_robin(
    db: Session,
    rule: AssignmentRule,
    logic: Dict[str, Any],
    *,
    dry_run: bool = False,
) -> Optional[UUID]:
    eligible_ids = _normalize_user_ids(logic.get("eligible_reps"))
    if not eligible_ids:
        logger.warning("Round-robin rule %s has no eligible reps", rule.id)
        return None

    max_leads = logic.get("max_leads_per_rep")
    last_index = (
        logic.get("state", {}).get("last_index")
        if isinstance(logic.get("state"), dict)
        else None
    )
    last_index = int(last_index) if isinstance(last_index, int) else -1

    active_counts = _load_active_assignment_counts(db, eligible_ids)

    ordered_candidates = list(eligible_ids)
    candidate_count = len(ordered_candidates)
    for step in range(candidate_count):
        next_index = (last_index + 1 + step) % candidate_count
        candidate_id = ordered_candidates[next_index]
        if max_leads is not None and active_counts.get(candidate_id, 0) >= max_leads:
            continue

        if not dry_run:
            # update state
            new_logic = dict(logic)
            new_state = dict(new_logic.get("state") or {})
            new_state["last_index"] = next_index
            new_state["last_assigned_user_id"] = str(candidate_id)
            new_logic["state"] = new_state
            rule.assignment_logic = new_logic
        return candidate_id

    logger.info("Round-robin rule %s skipped: all reps at capacity", rule.id)
    return None


def _assign_by_territory(db: Session, rule: AssignmentRule, logic: Dict[str, Any], lead: Lead) -> Optional[UUID]:
    territory_mapping = logic.get("territory_mapping") or {}
    lead_location = (lead.location or "").strip().lower()
    eligible_ids = None

    if lead_location:
        for territory, reps in territory_mapping.items():
            if lead_location == territory.strip().lower():
                eligible_ids = _normalize_user_ids(reps)
                break

    if not eligible_ids:
        eligible_ids = _normalize_user_ids(logic.get("eligible_reps"))

    if not eligible_ids:
        logger.info("Territory rule %s had no eligible reps for location '%s'", rule.id, lead.location)
        return None

    max_leads = logic.get("max_leads_per_rep")
    counts = _load_active_assignment_counts(db, eligible_ids)

    # Pick rep with fewest active leads (ties broken by UUID sorting)
    sorted_candidates = sorted(eligible_ids, key=lambda uid: (counts.get(uid, 0), str(uid)))
    for candidate in sorted_candidates:
        if max_leads is not None and counts.get(candidate, 0) >= max_leads:
            continue
        return candidate

    logger.info(
        "Territory rule %s skipped: all reps at capacity for location '%s'", rule.id, lead.location
    )
    return None


def _assign_by_workload(db: Session, rule: AssignmentRule, logic: Dict[str, Any]) -> Optional[UUID]:
    eligible_ids = _normalize_user_ids(logic.get("eligible_reps"))
    if not eligible_ids:
        # default to all active sales reps
        eligible_ids = [
            user.id
            for user in db.query(User)
            .filter(User.role == UserRole.SALES_REP.value, User.is_active.is_(True))
            .all()
        ]

    if not eligible_ids:
        logger.info("Workload rule %s found no eligible reps", rule.id)
        return None

    max_leads = logic.get("max_leads_per_rep")
    counts = _load_active_assignment_counts(db, eligible_ids)

    sorted_candidates = sorted(eligible_ids, key=lambda uid: (counts.get(uid, 0), str(uid)))
    for candidate in sorted_candidates:
        if max_leads is not None and counts.get(candidate, 0) >= max_leads:
            continue
        return candidate

    logger.info("Workload rule %s skipped: all reps at capacity", rule.id)
    return None


def _assign_by_score(db: Session, rule: AssignmentRule, logic: Dict[str, Any], lead: Lead) -> Optional[UUID]:
    tiers: Iterable[Dict[str, Any]] | None = logic.get("tiers")
    fallback_reps = _normalize_user_ids(logic.get("fallback_reps"))
    score = lead.current_score or 0

    if tiers:
        for tier in tiers:
            min_score = tier.get("min_score", 0)
            max_score = tier.get("max_score", 100)
            if min_score <= score <= max_score:
                tier_reps = _normalize_user_ids(tier.get("reps"))
                if tier_reps:
                    selected = _pick_lowest_workload(db, tier_reps, tier.get("max_leads_per_rep"))
                    if selected:
                        return selected

    if fallback_reps:
        return _pick_lowest_workload(db, fallback_reps, logic.get("max_leads_per_rep"))

    logger.info("Score-based rule %s had no matching tier for lead %s", rule.id, lead.id)
    return None


def _pick_lowest_workload(db: Session, candidates: List[UUID], max_leads: Optional[int]) -> Optional[UUID]:
    counts = _load_active_assignment_counts(db, candidates)
    sorted_candidates = sorted(candidates, key=lambda uid: (counts.get(uid, 0), str(uid)))
    for candidate in sorted_candidates:
        if max_leads is not None and counts.get(candidate, 0) >= max_leads:
            continue
        return candidate
    return None


def _normalize_user_ids(values: Any) -> List[UUID]:
    if not values:
        return []

    normalized: List[UUID] = []
    for value in values:
        try:
            normalized.append(UUID(str(value)))
        except (ValueError, TypeError):
            logger.warning("Invalid user ID %s encountered in assignment logic", value)
    return normalized


def _load_active_assignment_counts(db: Session, user_ids: Iterable[UUID]) -> Dict[UUID, int]:
    user_ids = list(user_ids)
    if not user_ids:
        return {}

    counts: Dict[UUID, int] = defaultdict(int)
    result = (
        db.query(LeadAssignment.user_id, func.count(LeadAssignment.id))
        .filter(
            LeadAssignment.user_id.in_(user_ids),
            LeadAssignment.status == "active",
        )
        .group_by(LeadAssignment.user_id)
        .all()
    )
    for user_id, count in result:
        counts[user_id] = int(count)
    return counts


def test_rule_against_lead(
    rule_id: int,
    lead_id: UUID,
    *,
    db: Session | None = None,
) -> Dict[str, Any]:
    """Evaluate a specific rule against a lead without mutating state."""
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        rule = db.query(AssignmentRule).filter(AssignmentRule.id == rule_id).one_or_none()
        if rule is None:
            return {"matches": False, "reason": "Rule not found"}

        lead = db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if lead is None:
            return {"matches": False, "reason": "Lead not found"}

        now = datetime.utcnow()
        if not _rule_matches_conditions(rule.conditions, lead, now):
            return {"matches": False, "reason": "Rule conditions did not match lead attributes"}

        suggested_user = _resolve_assignment(db, rule, lead, now, dry_run=True)
        response: Dict[str, Any] = {
            "matches": True,
            "rule_id": rule_id,
            "lead_id": str(lead_id),
        }

        if suggested_user:
            user = db.query(User).filter(User.id == suggested_user).one_or_none()
            response["assigned_user_id"] = str(suggested_user)
            if user:
                response["assigned_user_name"] = user.full_name
        else:
            response["assigned_user_id"] = None
            response["reason"] = "No eligible representative available"

        return response
    finally:
        if owns_session:
            db.close()


def apply_rule_to_lead(
    rule_id: int,
    lead_id: UUID,
    *,
    db: Session | None = None,
) -> Dict[str, Any]:
    """Apply a specific rule to a lead and create an assignment if possible."""
    owns_session = False
    if db is None:
        db = SessionLocal()
        owns_session = True

    try:
        rule = db.query(AssignmentRule).filter(AssignmentRule.id == rule_id).one_or_none()
        if rule is None:
            return {"success": False, "message": "Rule not found"}

        lead = db.query(Lead).filter(Lead.id == lead_id).one_or_none()
        if lead is None:
            return {"success": False, "message": "Lead not found"}

        if not rule.active:
            return {"success": False, "message": "Rule is inactive"}

        if _has_active_assignment(db, lead_id):
            return {"success": False, "message": "Lead already has an active assignment"}

        now = datetime.utcnow()
        if not _rule_matches_conditions(rule.conditions, lead, now):
            return {"success": False, "message": "Rule conditions did not match lead attributes"}

        assignee_id = _resolve_assignment(db, rule, lead, now, dry_run=False)
        if assignee_id is None:
            return {"success": False, "message": "No eligible representative available"}

        assignment = LeadAssignment(
            lead_id=lead.id,
            user_id=assignee_id,
            assigned_by=None,
            notes=f"Auto-assigned via rule: {rule.name}",
            is_primary=True,
        )
        db.add(assignment)
        db.add(rule)
        db.flush()

        assigned_user = db.query(User).filter(User.id == assignee_id).one_or_none()
        if assigned_user is None:
            db.rollback()
            return {"success": False, "message": "Assigned user no longer exists"}

        db.commit()

        try:
            notification_service.notify_lead_assigned(db, assigned_user, lead, send_email=True)
        except Exception:  # pragma: no cover - notification failure shouldn't stop success
            logger.exception("Failed to send notification after applying rule %s", rule_id)

        return {
            "success": True,
            "assigned_user_id": str(assignee_id),
            "assigned_user_name": assigned_user.full_name,
        }
    except Exception:
        db.rollback()
        logger.exception("Failed to apply assignment rule %s to lead %s", rule_id, lead_id)
        return {"success": False, "message": "Unexpected error while applying rule"}
    finally:
        if owns_session:
            db.close()

