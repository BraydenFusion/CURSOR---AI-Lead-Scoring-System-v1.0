"""Authentication and authorization utilities."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

from ..config import get_settings

settings = get_settings()

# Configuration - loaded from environment variables
SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# Validate SECRET_KEY in production
if settings.environment == "production" and SECRET_KEY == "DEV-ONLY-CHANGE-IN-PRODUCTION-use-long-random-string-here":
    raise ValueError(
        "CRITICAL: SECRET_KEY must be changed in production! "
        "Set SECRET_KEY environment variable to a long random string."
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify password against hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password. Bcrypt has a 72-byte limit, so truncate if necessary."""
    # Bcrypt has a 72-byte limit, so truncate password if it's longer
    # This is safe because we validate password strength before hashing
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
        password = password_bytes.decode('utf-8', errors='ignore')
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token with security best practices.
    
    Security features:
    - Expiration time (default 30 minutes)
    - Issued at time (iat)
    - Not before time (nbf)
    - JWT ID (jti) for token revocation
    """
    import secrets
    
    to_encode = data.copy()

    now = datetime.utcnow()
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    # SECURITY: Add standard JWT claims
    to_encode.update({
        "exp": expire,  # Expiration time
        "iat": now,  # Issued at
        "nbf": now,  # Not before (token valid from now)
        "jti": secrets.token_hex(16),  # JWT ID for revocation tracking
        "type": "access",  # Token type
    })
    
    # SECURITY: Use HS256 algorithm (already set, but explicit)
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> TokenData:
    """
    Decode and verify JWT token with security checks.
    
    Security features:
    - Algorithm verification (only HS256)
    - Expiration check
    - Token type validation
    - Not before check
    """
    try:
        # SECURITY: Explicitly specify algorithm to prevent algorithm confusion attacks
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],  # Only accept HS256
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_nbf": True,
                "require": ["exp", "iat", "nbf"]  # Require standard claims
            }
        )
        
        # SECURITY: Verify token type
        token_type = payload.get("type")
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
            )
        
        user_id: str = payload.get("sub")
        username: str = payload.get("username")
        role_str: str = payload.get("role")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
            )

        from app.models.user import UserRole
        
        # Convert string role to UserRole enum
        role = UserRole(role_str) if role_str else None

        return TokenData(user_id=UUID(user_id), username=username, role=role)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
    except (JWTError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """Get current authenticated user from token."""
    token_data = decode_access_token(token)

    user = db.query(User).filter(User.id == token_data.user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """Get current active user."""
    return current_user


def require_role(allowed_roles: list):
    """Decorator to require specific roles."""

    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.get_role_enum() not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required roles: {allowed_roles}",
            )
        return current_user

    return role_checker


def create_password_reset_token(email: str) -> str:
    """Create a password reset token."""
    expire = datetime.utcnow() + timedelta(hours=1)  # 1 hour expiry
    data = {
        "sub": email,
        "exp": expire,
        "type": "password_reset",
    }
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)


def verify_password_reset_token(token: str) -> str | None:
    """Verify password reset token and return email."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        token_type = payload.get("type")

        if token_type != "password_reset" or email is None:
            return None

        return email
    except JWTError:
        return None

