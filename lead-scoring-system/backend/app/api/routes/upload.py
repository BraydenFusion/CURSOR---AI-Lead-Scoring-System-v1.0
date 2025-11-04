"""Lead upload routes for CSV and individual lead uploads."""

import csv
import io
from typing import List
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.lead import Lead, LeadStatus
from ...models.user import User
from ...schemas.lead import LeadCreate, LeadRead
from ...services.ai_scoring import calculate_overall_score
from ...utils.auth import get_current_active_user


router = APIRouter()


@router.post("/csv", response_model=dict, status_code=status.HTTP_201_CREATED)
async def upload_csv_leads(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """
    Upload leads from CSV file.
    
    Expected CSV format:
    - name, email, phone, source, location (optional)
    - First row should be headers
    - Phone and location are optional
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    try:
        # Read CSV content
        contents = await file.read()
        csv_content = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        created_leads = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 (row 1 is header)
            try:
                # Validate required fields
                if not row.get('name') or not row.get('email'):
                    errors.append({
                        "row": row_num,
                        "error": "Missing required fields: name and email are required"
                    })
                    continue
                
                # Check if email already exists
                existing = db.query(Lead).filter(Lead.email == row['email'].strip()).first()
                if existing:
                    errors.append({
                        "row": row_num,
                        "error": f"Lead with email {row['email']} already exists"
                    })
                    continue
                
                # Create lead
                lead = Lead(
                    id=uuid4(),
                    name=row['name'].strip(),
                    email=row['email'].strip(),
                    phone=row.get('phone', '').strip() or None,
                    source=row.get('source', 'csv_upload').strip() or 'csv_upload',
                    location=row.get('location', '').strip() or None,
                    created_by=current_user.id,
                    current_score=0,
                    classification=None,
                    status=LeadStatus.NEW,
                    _metadata={
                        "upload_source": "csv",
                        "uploaded_by": current_user.username,
                        "original_row": row_num
                    }
                )
                
                db.add(lead)
                db.flush()
                
                # Score the lead with AI
                try:
                    calculate_overall_score(lead.id, db, use_openai=True)
                except Exception as e:
                    # Continue even if scoring fails
                    pass
                
                db.refresh(lead)
                created_leads.append({
                    "id": str(lead.id),
                    "name": lead.name,
                    "email": lead.email,
                    "score": lead.current_score,
                    "classification": lead.classification
                })
                
            except Exception as e:
                errors.append({
                    "row": row_num,
                    "error": str(e)
                })
        
        db.commit()
        
        return {
            "message": f"Successfully processed {len(created_leads)} leads",
            "created": len(created_leads),
            "errors": len(errors),
            "leads": created_leads,
            "error_details": errors
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing CSV: {str(e)}"
        )


@router.post("/individual", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
def create_individual_lead(
    payload: LeadCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> LeadRead:
    """Create a single lead and automatically score it with AI."""
    
    try:
        # Check if email already exists
        existing_lead = db.query(Lead).filter(Lead.email == payload.email).first()
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Lead with email {payload.email} already exists"
            )

        # Create new lead with ownership
        lead = Lead(
            id=uuid4(),
            name=payload.name,
            email=payload.email,
            phone=payload.phone,
            source=payload.source,
            location=payload.location,
            created_by=current_user.id,
            _metadata={**payload.metadata, "upload_source": "individual", "uploaded_by": current_user.username},
            current_score=0,
            classification=None,
            status=LeadStatus.NEW,
        )

        db.add(lead)
        db.flush()

        # Calculate initial score using AI scoring
        try:
            calculate_overall_score(lead.id, db, use_openai=True)
        except Exception:
            # Fallback to rule-based scoring if AI scoring fails
            from ...services.scoring_service import calculate_lead_score
            calculate_lead_score(lead.id, db)

        # Refresh to get updated score
        db.refresh(lead)

        # Convert to dict format
        lead_dict = {
            "id": lead.id,
            "name": lead.name,
            "email": lead.email,
            "phone": lead.phone,
            "source": lead.source,
            "location": lead.location,
            "metadata": lead._metadata if hasattr(lead, '_metadata') else {},
            "current_score": lead.current_score,
            "classification": lead.classification,
            "status": lead.status,
            "contacted_at": lead.contacted_at,
            "qualified_at": lead.qualified_at,
            "closed_at": lead.closed_at,
            "created_at": lead.created_at,
            "updated_at": lead.updated_at,
        }
        return LeadRead.model_validate(lead_dict)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating lead: {str(e)}"
        )

