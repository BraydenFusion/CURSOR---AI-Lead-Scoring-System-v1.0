"""Security utilities for input validation, sanitization, and security checks."""

import re
import os
from typing import Optional
from email.utils import parseaddr
import html

# Maximum file size for uploads (10MB)
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Allowed file extensions for uploads
ALLOWED_EXTENSIONS = {'.csv'}

# Maximum CSV rows to process at once
MAX_CSV_ROWS = 1000

# Maximum string lengths
MAX_NAME_LENGTH = 255
MAX_EMAIL_LENGTH = 255
MAX_PHONE_LENGTH = 50
MAX_SOURCE_LENGTH = 100
MAX_LOCATION_LENGTH = 255


def sanitize_string(input_str: str, max_length: Optional[int] = None) -> str:
    """
    Sanitize string input to prevent XSS and injection attacks.
    
    Args:
        input_str: Input string to sanitize
        max_length: Maximum allowed length (raises ValueError if exceeded)
    
    Returns:
        Sanitized string
    """
    if not isinstance(input_str, str):
        raise ValueError("Input must be a string")
    
    # Remove null bytes
    sanitized = input_str.replace('\x00', '')
    
    # HTML escape to prevent XSS
    sanitized = html.escape(sanitized)
    
    # Strip whitespace
    sanitized = sanitized.strip()
    
    # Check length
    if max_length and len(sanitized) > max_length:
        raise ValueError(f"Input exceeds maximum length of {max_length} characters")
    
    return sanitized


def sanitize_email(email: str) -> str:
    """
    Validate and sanitize email address.
    
    Args:
        email: Email address to validate
    
    Returns:
        Sanitized email address
    
    Raises:
        ValueError: If email is invalid
    """
    if not email:
        raise ValueError("Email cannot be empty")
    
    # Parse email address
    name, addr = parseaddr(email)
    
    # Use the address part
    email = addr if addr else email
    
    # Remove whitespace
    email = email.strip().lower()
    
    # Basic email validation regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        raise ValueError("Invalid email format")
    
    # Check length
    if len(email) > MAX_EMAIL_LENGTH:
        raise ValueError(f"Email exceeds maximum length of {MAX_EMAIL_LENGTH} characters")
    
    return email


def sanitize_phone(phone: Optional[str]) -> Optional[str]:
    """
    Sanitize phone number.
    
    Args:
        phone: Phone number to sanitize
    
    Returns:
        Sanitized phone number or None
    """
    if not phone:
        return None
    
    # Remove all non-digit characters except + and spaces
    sanitized = re.sub(r'[^\d\+\s\-\(\)]', '', phone.strip())
    
    # Check length
    if len(sanitized) > MAX_PHONE_LENGTH:
        raise ValueError(f"Phone number exceeds maximum length of {MAX_PHONE_LENGTH} characters")
    
    return sanitized if sanitized else None


def validate_filename(filename: str) -> bool:
    """
    Validate filename to prevent directory traversal and other attacks.
    
    Args:
        filename: Filename to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not filename:
        return False
    
    # Check for directory traversal attempts
    if '..' in filename or '/' in filename or '\\' in filename:
        return False
    
    # Check file extension
    _, ext = os.path.splitext(filename.lower())
    if ext not in ALLOWED_EXTENSIONS:
        return False
    
    # Check filename length
    if len(filename) > 255:
        return False
    
    return True


def validate_file_size(file_size: int) -> bool:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
    
    Returns:
        True if valid, False otherwise
    """
    return 0 < file_size <= MAX_FILE_SIZE


def sanitize_csv_field(field_value: str, field_type: str = "text") -> str:
    """
    Sanitize CSV field value.
    
    Args:
        field_value: Field value to sanitize
        field_type: Type of field (text, email, phone)
    
    Returns:
        Sanitized field value
    """
    if not field_value:
        return ""
    
    # Strip whitespace
    field_value = field_value.strip()
    
    # Sanitize based on field type
    if field_type == "email":
        return sanitize_email(field_value)
    elif field_type == "phone":
        sanitized = sanitize_phone(field_value)
        return sanitized if sanitized else ""
    else:
        # Text field - sanitize HTML but don't escape (CSV is not HTML)
        # Just remove dangerous characters
        sanitized = field_value.replace('\x00', '').replace('\r', '')
        # Limit length
        if len(sanitized) > MAX_NAME_LENGTH:
            sanitized = sanitized[:MAX_NAME_LENGTH]
        return sanitized


def validate_csv_row_count(row_count: int) -> bool:
    """
    Validate CSV row count to prevent DoS attacks.
    
    Args:
        row_count: Number of rows in CSV
    
    Returns:
        True if valid, False otherwise
    """
    return 0 < row_count <= MAX_CSV_ROWS


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a secure random token.
    
    Args:
        length: Token length in bytes
    
    Returns:
        Hexadecimal token string
    """
    import secrets
    return secrets.token_hex(length)


def is_secure_password(password: str) -> tuple[bool, str]:
    """
    Check if password meets security requirements.
    
    Args:
        password: Password to check
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    # Check for common patterns
    common_patterns = [
        r'(.)\1{2,}',  # Repeated characters (aaa)
        r'(012|123|234|345|456|567|678|789)',  # Sequential numbers
        r'(abc|bcd|cde|def|efg|fgh|ghi|hij|ijk|jkl|klm|lmn|mno|nop|opq|pqr|qrs|rst|stu|tuv|uvw|vwx|wxy|xyz)',  # Sequential letters
    ]
    
    for pattern in common_patterns:
        if re.search(pattern, password.lower()):
            return False, "Password contains insecure patterns"
    
    return True, ""


def rate_limit_key(request: "Request", identifier: str = "ip") -> str:
    """
    Generate rate limit key from request.
    
    Args:
        request: FastAPI request object
        identifier: Identifier type (ip, user_id)
    
    Returns:
        Rate limit key
    """
    if identifier == "ip":
        # Get client IP (considering proxies)
        client_ip = request.client.host
        if forwarded_for := request.headers.get("X-Forwarded-For"):
            client_ip = forwarded_for.split(",")[0].strip()
        return f"rate_limit:ip:{client_ip}"
    elif identifier == "user_id":
        # This would be used with authenticated endpoints
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"rate_limit:user:{user_id}"
    return f"rate_limit:unknown:{request.client.host}"


def validate_origin(request: "Request", allowed_origins: list[str]) -> bool:
    """
    Validate request origin.
    
    Args:
        request: FastAPI request object
        allowed_origins: List of allowed origins
    
    Returns:
        True if origin is allowed, False otherwise
    """
    origin = request.headers.get("Origin")
    if not origin:
        return False
    
    return origin in allowed_origins

