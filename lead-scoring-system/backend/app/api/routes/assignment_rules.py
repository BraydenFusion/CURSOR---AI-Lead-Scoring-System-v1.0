"""API routes for managing assignment rules."""

from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AssignmentRule, UserRole, User, LeadAssignment
from app.schemas import (
    AssignmentRuleCreate,
    AssignmentRuleRead,
    AssignmentRuleTestResponse,
    AssignmentRuleToggleRequest,
    AssignmentRuleUpdate,
    AssignmentEligibleRep,
    AssignmentRuleApplyRequest,
    AssignmentRuleApplyResponse,
)
from app.services import test_rule_against_lead, apply_rule_to_lead
from app.utils.auth import require_role

router = APIRouter()


def _validate_user_ids(db: Session, user_ids: List[UUID]) -> None:
    if not user_ids:
        return
    existing = (
        db.query(User.id)
        .filter(
            User.id.in_(user_ids),
            User.is_active.is_(True),
            User.role == UserRole.SALES_REP.value,
        )
        .all()
    )
    existing_ids = {row[0] for row in existing}
    missing = [str(uid) for uid in user_ids if uid not in existing_ids]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unknown or inactive user IDs: {', '.join(missing)}",
        )


def _collect_user_ids_from_logic(logic_dict: dict) -> List[UUID]:
    user_ids: List[UUID] = []
    logic_type = logic_dict.get("type")

    if logic_type == "round_robin":
        user_ids.extend(logic_dict.get("eligible_reps", []))
    elif logic_type == "territory":
        user_ids.extend(logic_dict.get("eligible_reps") or [])
        territory_mapping = logic_dict.get("territory_mapping") or {}
        for reps in territory_mapping.values():
            user_ids.extend(reps or [])
    elif logic_type == "workload":
        user_ids.extend(logic_dict.get("eligible_reps") or [])
    elif logic_type == "score_based":
        for tier in logic_dict.get("tiers", []):
            user_ids.extend(tier.get("reps") or [])
        user_ids.extend(logic_dict.get("fallback_reps") or [])

    # Deduplicate while preserving order
    seen: set[UUID] = set()
    ordered: List[UUID] = []
    for raw_id in user_ids:
        try:
            parsed = UUID(str(raw_id))
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid UUID in assignment logic: {raw_id}",
            )
        if parsed not in seen:
            seen.add(parsed)
            ordered.append(parsed)
    return ordered


@router.get(
    "",
    response_model=List[AssignmentRuleRead],
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
def list_assignment_rules(
    db: Session = Depends(get_db),
) -> List[AssignmentRuleRead]:
    """List all assignment rules ordered by priority."""
    rules = (
        db.query(AssignmentRule)
        .order_by(AssignmentRule.priority.desc(), AssignmentRule.created_at.asc())
        .all()
    )
    return [AssignmentRuleRead.model_validate(rule) for rule in rules]


@router.post(
    "",
    response_model=AssignmentRuleRead,
    status_code=status.HTTP_201_CREATED,
)
def create_assignment_rule(
    payload: AssignmentRuleCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
) -> AssignmentRuleRead:
    """Create a new assignment rule."""
    existing = db.query(AssignmentRule).filter(AssignmentRule.name == payload.name).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rule name already exists.")

    logic_data = payload.assignment_logic.model_dump(mode="json", exclude_none=True)
    conditions_data = payload.conditions.model_dump(mode="json", exclude_none=True)

    _validate_user_ids(db, _collect_user_ids_from_logic(logic_data))

    rule = AssignmentRule(
        name=payload.name,
        description=payload.description,
        active=payload.active,
        priority=payload.priority,
        rule_type=payload.rule_type,
        conditions=conditions_data,
        assignment_logic=logic_data,
        created_by_id=current_user.id,
    )
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return AssignmentRuleRead.model_validate(rule)


@router.put(
    "/{rule_id}",
    response_model=AssignmentRuleRead,
)
def update_assignment_rule(
    rule_id: int,
    payload: AssignmentRuleUpdate,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
) -> AssignmentRuleRead:
    """Update an assignment rule."""
    rule = db.query(AssignmentRule).filter(AssignmentRule.id == rule_id).one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment rule not found.")

    if payload.name and payload.name != rule.name:
        existing = db.query(AssignmentRule).filter(AssignmentRule.name == payload.name).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Rule name already exists.")

    if payload.rule_type and payload.rule_type != rule.rule_type:
        rule.rule_type = payload.rule_type

    if payload.assignment_logic:
        logic_data = payload.assignment_logic.model_dump(mode="json", exclude_none=True)
        _validate_user_ids(db, _collect_user_ids_from_logic(logic_data))
        rule.assignment_logic = logic_data

    if payload.conditions:
        rule.conditions = payload.conditions.model_dump(mode="json", exclude_none=True)

    if payload.name is not None:
        rule.name = payload.name
    if payload.description is not None:
        rule.description = payload.description
    if payload.priority is not None:
        rule.priority = payload.priority
    if payload.active is not None:
        rule.active = payload.active

    db.add(rule)
    db.commit()
    db.refresh(rule)
    return AssignmentRuleRead.model_validate(rule)


@router.delete(
    "/{rule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_assignment_rule(
    rule_id: int,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
) -> Response:
    """Delete an assignment rule."""
    rule = db.query(AssignmentRule).filter(AssignmentRule.id == rule_id).one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment rule not found.")
    db.delete(rule)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{rule_id}/toggle",
    response_model=AssignmentRuleRead,
)
def toggle_assignment_rule(
    rule_id: int,
    payload: AssignmentRuleToggleRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
) -> AssignmentRuleRead:
    """Enable or disable an assignment rule."""
    rule = db.query(AssignmentRule).filter(AssignmentRule.id == rule_id).one_or_none()
    if not rule:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Assignment rule not found.")
    rule.active = payload.active
    db.add(rule)
    db.commit()
    db.refresh(rule)
    return AssignmentRuleRead.model_validate(rule)


@router.get(
    "/{rule_id}/test",
    response_model=AssignmentRuleTestResponse,
)
def test_assignment_rule(
    rule_id: int,
    lead_id: UUID = Query(..., description="ID of the lead to test against"),
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
) -> AssignmentRuleTestResponse:
    """Evaluate an assignment rule against a specific lead."""
    result = test_rule_against_lead(rule_id=rule_id, lead_id=lead_id, db=db)
    return AssignmentRuleTestResponse.model_validate(result)


@router.post(
    "/{rule_id}/apply",
    response_model=AssignmentRuleApplyResponse,
)
def apply_assignment_rule(
    rule_id: int,
    payload: AssignmentRuleApplyRequest,
    db: Session = Depends(get_db),
    _current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
) -> AssignmentRuleApplyResponse:
    """Apply a specific assignment rule to a lead."""
    result = apply_rule_to_lead(rule_id=rule_id, lead_id=payload.lead_id, db=db)
    return AssignmentRuleApplyResponse.model_validate(result)


@router.get(
    "/eligible-reps",
    response_model=List[AssignmentEligibleRep],
    dependencies=[Depends(require_role([UserRole.ADMIN, UserRole.MANAGER]))],
)
def list_eligible_representatives(
    db: Session = Depends(get_db),
) -> List[AssignmentEligibleRep]:
    """Return active sales representatives with current workload."""
    reps = (
        db.query(
            User.id,
            User.full_name,
            User.email,
            sa.func.count(LeadAssignment.id).label("active_assignments"),
        )
        .outerjoin(
            LeadAssignment,
            sa.and_(
                LeadAssignment.user_id == User.id,
                LeadAssignment.status == "active",
            ),
        )
        .filter(
            User.role == UserRole.SALES_REP.value,
            User.is_active.is_(True),
        )
        .group_by(User.id, User.full_name, User.email)
        .order_by(User.full_name.asc())
        .all()
    )
    return [
        AssignmentEligibleRep(
            id=row.id,
            full_name=row.full_name,
            email=row.email,
            active_assignments=row.active_assignments or 0,
        )
        for row in reps
    ]
