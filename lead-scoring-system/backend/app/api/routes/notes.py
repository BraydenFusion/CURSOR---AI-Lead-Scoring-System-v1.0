"""Lead notes routes for managing notes on leads."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.lead import Lead
from app.models.note import LeadNote
from app.models.user import User
from app.schemas.note import NoteCreate, NoteResponse
from app.utils.auth import get_current_active_user

router = APIRouter()


@router.post("/", response_model=NoteResponse, status_code=201)
def create_note(
    note_data: NoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Create a note for a lead."""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == note_data.lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Create note
    note = LeadNote(
        lead_id=note_data.lead_id,
        user_id=current_user.id,
        note_type=note_data.note_type,
        content=note_data.content,
    )

    db.add(note)
    db.commit()
    db.refresh(note)

    # Add user name for response
    response = NoteResponse.model_validate(note)
    response.user_name = current_user.full_name

    return response


@router.get("/{lead_id}", response_model=list[NoteResponse])
def get_lead_notes(
    lead_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get all notes for a lead."""
    # Verify lead exists
    lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    # Get notes with user info
    from app.models.user import User

    notes = (
        db.query(LeadNote, User.full_name)
        .join(User, LeadNote.user_id == User.id)
        .filter(LeadNote.lead_id == lead_id)
        .order_by(LeadNote.created_at.desc())
        .all()
    )

    return [
        NoteResponse(
            **note.__dict__,
            user_name=user_name,
        )
        for note, user_name in notes
    ]


@router.delete("/{note_id}", status_code=204)
def delete_note(
    note_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Delete a note (only author can delete)."""
    note = db.query(LeadNote).filter(LeadNote.id == note_id).first()

    if not note:
        raise HTTPException(status_code=404, detail="Note not found")

    # Only author or admin can delete
    if note.user_id != current_user.id and current_user.role.value != "admin":
        raise HTTPException(status_code=403, detail="Permission denied")

    db.delete(note)
    db.commit()

    return None

