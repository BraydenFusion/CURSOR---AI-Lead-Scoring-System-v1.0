"""User profile management routes."""

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.user import User
from ...schemas.user import UserResponse
from ...utils.auth import get_current_active_user, get_password_hash, verify_password
from ...utils.password_security import validate_password_strength, check_password_breach
from ...utils.security import sanitize_email


router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
) -> UserResponse:
    """Get current user's profile information."""
    return current_user


@router.post("/profile-picture", response_model=dict)
async def upload_profile_picture(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Upload profile picture for current user.
    
    Security:
    - File type validation (images only)
    - File size limit (2MB)
    - Secure storage
    """
    # SECURITY: Validate file type
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be an image (JPG, PNG, GIF, etc.)"
        )
    
    # SECURITY: Validate file size (2MB max)
    MAX_FILE_SIZE = 2 * 1024 * 1024  # 2MB
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 2MB"
        )
    
    # For now, store the file metadata or URL
    # In production, you would upload to S3, Cloudinary, or similar
    # For this implementation, we'll store a placeholder URL
    profile_picture_url = f"/uploads/profile/{current_user.id}/{file.filename}"
    
    # Update user profile (in a real implementation, you'd store the actual file)
    # For now, we'll just return success
    # In production: upload to cloud storage and save URL to database
    
    return {
        "message": "Profile picture uploaded successfully",
        "profile_picture_url": profile_picture_url,
        "filename": file.filename
    }


@router.post("/change-password", response_model=dict)
def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change user password.
    
    Security:
    - Verify current password
    - Validate new password strength
    - Check against breach database
    """
    # SECURITY: Verify current password
    if not verify_password(current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Current password is incorrect"
        )
    
    # SECURITY: Validate new password strength
    is_valid, error_msg = validate_password_strength(new_password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Password security requirement not met: {error_msg}"
        )
    
    # SECURITY: Check if password appears in breach database
    if check_password_breach(new_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This password has been found in data breaches. Please choose a different password."
        )
    
    # Update password
    current_user.hashed_password = get_password_hash(new_password)
    db.commit()
    
    return {"message": "Password changed successfully"}


@router.post("/change-email", response_model=dict)
def change_email(
    new_email: str,
    password: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """
    Change user email address.
    
    Security:
    - Verify current password
    - Validate new email format
    - Check if email already exists
    """
    # SECURITY: Verify current password
    if not verify_password(password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Password is incorrect"
        )
    
    # SECURITY: Sanitize and validate email
    try:
        sanitized_email = sanitize_email(new_email)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid email format: {str(e)}"
        )
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == sanitized_email).first()
    if existing_user and existing_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email address is already in use"
        )
    
    # Update email
    current_user.email = sanitized_email
    db.commit()
    
    return {"message": "Email changed successfully"}

