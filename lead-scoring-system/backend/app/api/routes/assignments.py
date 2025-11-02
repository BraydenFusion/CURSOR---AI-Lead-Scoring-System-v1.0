"""Lead assignment routes for managing lead assignments to users."""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.assignment import LeadAssignment
from app.models.lead import Lead
from app.models.user import User, UserRole
from app.schemas.assignment import AssignmentCreate, AssignmentResponse, AssignmentWithDetails
from app.utils.auth import get_current_active_user, require_role
from app.services.notification_service import notification_service

router = APIRouter()


@router.post("/", response_model=AssignmentResponse, status_code=201)
def assign_lead(
    assignment_data: AssignmentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    """Assign a lead to a sales rep (Admin/Manager only)."""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == assignment_data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Verify user exists and is a sales rep
    user = db.query(User).filter(User.id == assignment_data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if already assigned
    existing = (
        db.query(LeadAssignment)
        .filter(
            LeadAssignment.lead_id == assignment_data.lead_id,
            LeadAssignment.user_id == assignment_data.user_id,
            LeadAssignment.status == "active",
        )
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Lead already assigned to this user")

    # Create assignment
    assignment = LeadAssignment(
        lead_id=assignment_data.lead_id,
        user_id=assignment_data.user_id,
        assigned_by=current_user.id,
        notes=assignment_data.notes,
        is_primary=assignment_data.is_primary,
    )

    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    # Send notification to assigned user
    notification_service.notify_lead_assigned(db, user, lead, send_email=True)

    return assignment


@router.get("/my-leads", response_model=List[AssignmentWithDetails])
def get_my_assigned_leads(
    status: Optional[str] = Query("active", regex="^(active|completed|transferred|all)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get leads assigned to current user."""
    query = (
        db.query(
            LeadAssignment,
            Lead.name.label("lead_name"),
            Lead.email.label("lead_email"),
            Lead.current_score.label("lead_score"),
        )
        .join(Lead, LeadAssignment.lead_id == Lead.id)
        .filter(LeadAssignment.user_id == current_user.id)
    )

    if status != "all":
        query = query.filter(LeadAssignment.status == status)

    results = query.order_by(Lead.current_score.desc()).all()

    return [
        {
            **assignment.__dict__,
            "lead_name": lead_name,
            "lead_email": lead_email,
            "lead_score": lead_score,
            "user_name": current_user.full_name,
            "user_email": current_user.email,
        }
        for assignment, lead_name, lead_email, lead_score in results
    ]


@router.get("/team-leads", response_model=List[AssignmentWithDetails])
def get_team_assignments(
    user_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    """Get all team assignments (Admin/Manager only)."""
    query = (
        db.query(
            LeadAssignment,
            Lead.name.label("lead_name"),
            Lead.email.label("lead_email"),
            Lead.current_score.label("lead_score"),
            User.full_name.label("user_name"),
            User.email.label("user_email"),
        )
        .join(Lead, LeadAssignment.lead_id == Lead.id)
        .join(User, LeadAssignment.user_id == User.id)
        .filter(LeadAssignment.status == "active")
    )

    if user_id:
        query = query.filter(LeadAssignment.user_id == user_id)

    results = query.order_by(Lead.current_score.desc()).all()

    return [
        {
            **assignment.__dict__,
            "lead_name": lead_name,
            "lead_email": lead_email,
            "lead_score": lead_score,
            "user_name": user_name,
            "user_email": user_email,
        }
        for assignment, lead_name, lead_email, lead_score, user_name, user_email in results
    ]


@router.delete("/{assignment_id}", status_code=204)
def unassign_lead(
    assignment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    """Remove lead assignment (Admin/Manager only)."""
    assignment = db.query(LeadAssignment).filter(LeadAssignment.id == assignment_id).first()

    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    assignment.status = "transferred"
    db.commit()

    return None


@router.get("/unassigned-leads", response_model=List[dict])
def get_unassigned_leads(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
):
    """Get leads that are not assigned to anyone."""
    # Get all lead IDs that have active assignments
    assigned_lead_ids = [
        result[0]
        for result in db.query(LeadAssignment.lead_id)
        .filter(LeadAssignment.status == "active")
        .distinct()
        .all()
    ]

    # Get leads not in that list
    if assigned_lead_ids:
        unassigned_leads = (
            db.query(Lead).filter(~Lead.id.in_(assigned_lead_ids)).order_by(Lead.current_score.desc()).all()
        )
    else:
        # If no assignments exist, all leads are unassigned
        unassigned_leads = db.query(Lead).order_by(Lead.current_score.desc()).all()

    return [
        {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "score": lead.current_score,
            "classification": lead.classification,
            "source": lead.source,
            "created_at": lead.created_at,
        }
        for lead in unassigned_leads
    ]

