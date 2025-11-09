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
from ...services import auto_assign_lead
from ...utils.auth import get_current_active_user
from ...utils.security import (
    validate_filename,
    validate_file_size,
    sanitize_email,
    sanitize_phone,
    sanitize_csv_field,
    validate_csv_row_count,
    MAX_CSV_ROWS,
)


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
    
    Security:
    - File size limited to 10MB
    - Maximum 1000 rows per upload
    - Filename validation to prevent directory traversal
    - Input sanitization for all fields
    """
    # SECURITY: Validate filename
    if not file.filename or not validate_filename(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid filename or file type. Only CSV files are allowed."
        )
    
    # SECURITY: Check file size before reading
    file_size = 0
    contents = b""
    try:
        contents = await file.read()
        file_size = len(contents)
        
        if not validate_file_size(file_size):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size exceeds maximum allowed size of 10MB"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Error reading file: {str(e)}"
        )
    
    try:
        # SECURITY: Validate encoding and decode safely
        try:
            csv_content = contents.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="File must be UTF-8 encoded"
            )
        
        # SECURITY: Limit CSV parsing to prevent DoS
        csv_reader = csv.DictReader(io.StringIO(csv_content))
        
        # Count rows first (with limit) - convert to list to check count
        rows = list(csv_reader)
        if not validate_csv_row_count(len(rows)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"CSV file contains too many rows. Maximum {MAX_CSV_ROWS} rows allowed."
            )
        
        created_leads = []
        errors = []
        
        # Process rows (already converted to list above)
        for row_num, row in enumerate(rows, start=2):  # Start at 2 (row 1 is header)
            try:
                # SECURITY: Sanitize and validate all inputs
                raw_name = row.get('name', '').strip()
                raw_email = row.get('email', '').strip()
                
                if not raw_name or not raw_email:
                    errors.append({
                        "row": row_num,
                        "error": "Missing required fields: name and email are required"
                    })
                    continue
                
                # SECURITY: Sanitize email
                try:
                    sanitized_email = sanitize_email(raw_email)
                except ValueError as e:
                    errors.append({
                        "row": row_num,
                        "error": f"Invalid email format: {str(e)}"
                    })
                    continue
                
                # SECURITY: Sanitize name
                try:
                    sanitized_name = sanitize_csv_field(raw_name, "text")
                    if len(sanitized_name) > 255:
                        sanitized_name = sanitized_name[:255]
                except ValueError as e:
                    errors.append({
                        "row": row_num,
                        "error": f"Invalid name: {str(e)}"
                    })
                    continue
                
                # SECURITY: Check if email already exists (after sanitization)
                existing = db.query(Lead).filter(Lead.email == sanitized_email).first()
                if existing:
                    errors.append({
                        "row": row_num,
                        "error": f"Lead with email {sanitized_email} already exists"
                    })
                    continue
                
                # SECURITY: Sanitize optional fields
                sanitized_phone = None
                if row.get('phone'):
                    try:
                        sanitized_phone = sanitize_phone(row.get('phone', ''))
                    except ValueError:
                        # Invalid phone, but not required, so continue
                        pass
                
                sanitized_source = sanitize_csv_field(row.get('source', 'csv_upload'), "text")
                if len(sanitized_source) > 100:
                    sanitized_source = sanitized_source[:100]
                if not sanitized_source:
                    sanitized_source = 'csv_upload'
                
                sanitized_location = None
                if row.get('location'):
                    sanitized_location = sanitize_csv_field(row.get('location', ''), "text")
                    if len(sanitized_location) > 255:
                        sanitized_location = sanitized_location[:255]
                    if not sanitized_location:
                        sanitized_location = None
                
                # Create lead with sanitized data
                lead = Lead(
                    id=uuid4(),
                    name=sanitized_name,
                    email=sanitized_email,
                    phone=sanitized_phone,
                    source=sanitized_source,
                    location=sanitized_location,
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
        # SECURITY: Sanitize and validate email
        try:
            sanitized_email = sanitize_email(payload.email)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid email format: {str(e)}"
            )
        
        # Check if email already exists
        existing_lead = db.query(Lead).filter(Lead.email == sanitized_email).first()
        if existing_lead:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Lead with email {sanitized_email} already exists"
            )

        # SECURITY: Sanitize name
        sanitized_name = sanitize_csv_field(payload.name, "text")
        if len(sanitized_name) > MAX_NAME_LENGTH:
            sanitized_name = sanitized_name[:MAX_NAME_LENGTH]
        
        # SECURITY: Sanitize phone
        sanitized_phone = None
        if payload.phone:
            try:
                sanitized_phone = sanitize_phone(payload.phone)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid phone number format"
                )
        
        # SECURITY: Sanitize source
        sanitized_source = sanitize_csv_field(payload.source or "manual_entry", "text")
        if len(sanitized_source) > 100:
            sanitized_source = sanitized_source[:100]
        
        # SECURITY: Sanitize location
        sanitized_location = None
        if payload.location:
            sanitized_location = sanitize_csv_field(payload.location, "text")
            if len(sanitized_location) > 255:
                sanitized_location = sanitized_location[:255]

        metadata = {
            **payload.metadata,
            "upload_source": "individual",
            "uploaded_by": current_user.username,
        }
        if not payload.auto_assign:
            metadata["auto_assignment_enabled"] = False

        # Create new lead with ownership and sanitized data
        lead = Lead(
            id=uuid4(),
            name=sanitized_name,
            email=sanitized_email,
            phone=sanitized_phone,
            source=sanitized_source,
            location=sanitized_location,
            created_by=current_user.id,
            _metadata=metadata,
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

        if payload.auto_assign:
            auto_assign_lead(lead.id, db=db)

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

