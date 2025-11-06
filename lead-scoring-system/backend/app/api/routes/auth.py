"""Authentication routes for user registration, login, and profile."""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import Token, UserCreate, UserResponse
from app.utils.auth import (
    create_access_token,
    create_password_reset_token,
    get_current_active_user,
    get_password_hash,
    verify_password,
    verify_password_reset_token,
)
from app.utils.password_security import (
    validate_password_strength,
    check_password_breach,
    PasswordSecurityError,
)
from app.services.email_service import email_service
from pydantic import BaseModel, EmailStr, Field

# Rate limiting (optional - will only work if slowapi is installed)
try:
    from app.middleware.rate_limit import rate_limit_strict
    rate_limit_decorator = rate_limit_strict
except ImportError:
    # If slowapi not installed, skip rate limiting
    def rate_limit_decorator(func):
        return func

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=201)
@rate_limit_decorator  # SECURITY: Rate limit registration to prevent abuse
def register_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user with high security password validation.
    
    Security features:
    - Password strength validation
    - Breach database checking
    - Rate limiting
    - Input sanitization
    """
    # SECURITY: Sanitize inputs
    from app.utils.security import sanitize_email, sanitize_string
    
    try:
        sanitized_email = sanitize_email(user_data.email)
        sanitized_username = sanitize_string(user_data.username, max_length=100)
        sanitized_full_name = sanitize_string(user_data.full_name, max_length=255)
        sanitized_company_role = sanitize_string(user_data.company_role, max_length=100) if user_data.company_role else None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: {str(e)}",
        )
    
    # HIGH SECURITY: Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Validation error: Password security requirement not met: {error_msg}",
        )
    
    # HIGH SECURITY: Check if password appears in breach database
    if check_password_breach(user_data.password):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation error: This password has been found in data breaches. Please choose a different password.",
        )
    
    # SECURITY: Check if user exists (use sanitized values)
    existing_user = db.query(User).filter(
        (User.email == sanitized_email) | (User.username == sanitized_username)
    ).first()

    if existing_user:
        # SECURITY: Don't reveal which field already exists (prevents user enumeration)
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Validation error: User with this email or username already exists",
        )
    
    # SECURITY: Use sanitized values
    user_data.email = sanitized_email
    user_data.username = sanitized_username
    user_data.full_name = sanitized_full_name

    # Create user with secure password hashing
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        full_name=user_data.full_name,
        hashed_password=hashed_password,
        role=user_data.role,  # SQLEnum will handle the conversion to PostgreSQL ENUM
        company_role=sanitized_company_role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
@rate_limit_decorator
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Login user and return JWT token."""
    # Import audit logger
    from app.utils.audit_logger import log_login_attempt
    
    # Get client IP for audit logging
    client_ip = request.client.host if request.client else "unknown"
    
    # Find user
    user = db.query(User).filter(User.username == form_data.username).first()

    if not user or not verify_password(form_data.password, user.hashed_password):
        log_login_attempt(form_data.username, success=False, ip_address=client_ip)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    # Log successful login
    log_login_attempt(form_data.username, success=True, ip_address=client_ip)

    # Create token
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "username": user.username,
            "role": user.get_role_enum().value,
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user,
    }


class GoogleAuthRequest(BaseModel):
    """Schema for Google authentication request."""
    
    id_token: str = Field(..., description="Google ID token from Firebase")


@router.post("/google", response_model=Token)
@rate_limit_decorator
def google_auth(
    request: Request,
    google_data: GoogleAuthRequest,
    db: Session = Depends(get_db),
):
    """
    Authenticate user with Google Sign-In.
    Verifies the Google ID token and creates/updates user account.
    """
    try:
        from google.auth.transport import requests
        from google.oauth2 import id_token
        from app.config import get_settings
        
        settings = get_settings()
        
        # Verify the Google ID token
        try:
            # Verify the token
            idinfo = id_token.verify_oauth2_token(
                google_data.id_token,
                requests.Request(),
                settings.google_client_id or "AIzaSyCQfvpghMDKoakqKQ2tx67gjjEo6JnmAbA"  # Use Firebase API key as client ID
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            # Extract user information
            google_email = idinfo['email']
            google_name = idinfo.get('name', '')
            google_picture = idinfo.get('picture')
            google_sub = idinfo['sub']  # Google user ID
            
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )
        
        # Check if user exists by email
        user = db.query(User).filter(User.email == google_email).first()
        
        if user:
            # Update user info if needed
            if google_picture and not user.profile_picture_url:
                user.profile_picture_url = google_picture
            if google_name and user.full_name != google_name:
                user.full_name = google_name
            user.last_login = datetime.utcnow()
            db.commit()
            db.refresh(user)
        else:
            # Create new user from Google account
            # Generate username from email (before @)
            username_base = google_email.split('@')[0]
            username = username_base
            counter = 1
            
            # Ensure username is unique
            while db.query(User).filter(User.username == username).first():
                username = f"{username_base}{counter}"
                counter += 1
            
            # Create user with Google account info
            # Note: No password needed for Google-authenticated users
            # We'll use a random secure password hash (user can't login with password)
            import secrets
            random_password = secrets.token_urlsafe(32)
            hashed_password = get_password_hash(random_password)
            
            new_user = User(
                email=google_email,
                username=username,
                full_name=google_name or username,
                hashed_password=hashed_password,  # Random password (not used for Google auth)
                role=UserRole.SALES_REP,  # SQLEnum will handle the conversion to PostgreSQL ENUM
                profile_picture_url=google_picture,
                last_login=datetime.utcnow(),
            )
            
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            user = new_user
        
        # Create JWT token
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "username": user.username,
                "role": user.get_role_enum().value,
            }
        )
        
        # Log successful login
        from app.utils.audit import log_login_attempt
        client_ip = request.client.host if request.client else "unknown"
        log_login_attempt(user.username, success=True, ip_address=client_ip, method="google")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user,
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information."""
    return current_user


@router.post("/logout")
def logout(current_user: User = Depends(get_current_active_user)):
    """Logout user (client should delete token)."""
    return {"message": "Successfully logged out"}


class ForgotPasswordRequest(BaseModel):
    """Schema for forgot password request."""

    email: EmailStr


class ResetPasswordRequest(BaseModel):
    """Schema for password reset request."""

    token: str
    new_password: str = Field(..., min_length=8, max_length=100)


@router.post("/forgot-password")
async def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Request password reset email."""
    user = db.query(User).filter(User.email == request.email).first()

    # Always return success to prevent email enumeration
    if user:
        token = create_password_reset_token(request.email)
        reset_link = f"http://localhost:5173/reset-password?token={token}"

        # Send email
        email_service.send_email(
            to_email=request.email,
            subject="Password Reset Request",
            body=f"""Hi {user.full_name},

You requested to reset your password. Click the link below:

{reset_link}

This link expires in 1 hour.

If you didn't request this, please ignore this email.

Best regards,
Lead Scoring System""",
            html_body=f"""
<html>
<body>
    <h2>Password Reset Request</h2>
    <p>Hi {user.full_name},</p>
    <p>You requested to reset your password. Click the link below:</p>
    <p><a href="{reset_link}" style="background-color: #4F46E5; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">Reset Password</a></p>
    <p><small>This link expires in 1 hour.</small></p>
    <p>If you didn't request this, please ignore this email.</p>
    <p>Best regards,<br>Lead Scoring System</p>
</body>
</html>
""",
        )

    return {"message": "If the email exists, a reset link has been sent"}


@router.post("/reset-password")
async def reset_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using token with high security validation."""
    email = verify_password_reset_token(request.token)

    if not email:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # HIGH SECURITY: Validate new password strength
    is_valid, error_msg = validate_password_strength(request.new_password)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=f"Password security requirement not met: {error_msg}",
        )
    
    # HIGH SECURITY: Check if password appears in breach database
    if check_password_breach(request.new_password):
        raise HTTPException(
            status_code=400,
            detail="This password has been found in data breaches. Please choose a different password.",
        )

    # Update password with secure hashing
    user.hashed_password = get_password_hash(request.new_password)
    db.commit()

    return {"message": "Password reset successful"}

