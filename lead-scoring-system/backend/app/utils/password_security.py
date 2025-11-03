"""High-security password validation and utilities."""

import os
import re
from typing import Tuple
import secrets
import hashlib

# Optional: zxcvbn for advanced password strength checking
try:
    from zxcvbn import zxcvbn
    ZXCVBN_AVAILABLE = True
except ImportError:
    ZXCVBN_AVAILABLE = False
    # Fallback if zxcvbn not available
    def zxcvbn(password: str):
        return {"score": 2, "feedback": {"suggestions": []}}


class PasswordSecurityError(Exception):
    """Custom exception for password security issues."""
    pass


def validate_password_strength(password: str) -> Tuple[bool, str]:
    """
    Validate password meets high security requirements.
    
    Returns:
        (is_valid, error_message)
    """
    if not password:
        return False, "Password is required"
    
    # Minimum length
    if len(password) < 12:
        return False, "Password must be at least 12 characters long"
    
    # Maximum length (prevent DoS)
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for common patterns
    common_passwords = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "password123", "admin", "letmein", "welcome", "monkey"
    ]
    password_lower = password.lower()
    for common in common_passwords:
        if common in password_lower:
            return False, f"Password cannot contain common words like '{common}'"
    
    # Check for username/email patterns
    if re.search(r'\b(admin|user|test|demo)\b', password_lower):
        return False, "Password cannot contain common account names"
    
    # Require uppercase
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    # Require lowercase
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    # Require digit
    if not re.search(r'\d', password):
        return False, "Password must contain at least one number"
    
    # Require special character
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:"\\|,.<>/?]', password):
        return False, "Password must contain at least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)"
    
    # Check for repeated characters (more than 3 in a row)
    if re.search(r'(.)\1{3,}', password):
        return False, "Password cannot contain the same character repeated more than 3 times"
    
    # Check for sequential patterns (abc, 123, etc.)
    sequences = ['abcdefghijklmnopqrstuvwxyz', '01234567890', 'qwertyuiop', 'asdfghjkl', 'zxcvbnm']
    password_lower = password.lower()
    for seq in sequences:
        for i in range(len(seq) - 2):
            if seq[i:i+3] in password_lower:
                return False, "Password cannot contain sequential characters (abc, 123, etc.)"
    
    # Use zxcvbn for advanced strength checking (if available)
    if ZXCVBN_AVAILABLE:
        try:
            result = zxcvbn(password)
            score = result.get('score', 0)
            
            # Require score of at least 3 (out of 4)
            if score < 3:
                feedback = result.get('feedback', {})
                suggestions = feedback.get('suggestions', [])
                if suggestions:
                    return False, f"Weak password. {suggestions[0]}"
                return False, "Password is too weak. Use a longer, more complex password."
        except Exception:
            # If zxcvbn fails, continue with basic checks
            pass
    
    return True, ""


def check_password_breach(password: str) -> bool:
    """
    Check if password appears in common breach databases.
    Uses SHA-1 hash prefix checking (Have I Been Pwned API concept).
    """
    # Simplified check - in production, use Have I Been Pwned API
    # For now, check against common breached passwords
    common_breached = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "password123", "admin123", "welcome123"
    ]
    
    password_lower = password.lower()
    for breached in common_breached:
        if password_lower == breached or breached in password_lower:
            return True
    
    return False


def generate_secure_password(length: int = 16) -> str:
    """Generate a cryptographically secure random password."""
    if length < 12:
        length = 12
    
    # Character sets
    uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    digits = "0123456789"
    special = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    all_chars = uppercase + lowercase + digits + special
    
    # Ensure at least one of each type
    password = [
        secrets.choice(uppercase),
        secrets.choice(lowercase),
        secrets.choice(digits),
        secrets.choice(special),
    ]
    
    # Fill the rest randomly
    for _ in range(length - 4):
        password.append(secrets.choice(all_chars))
    
    # Shuffle
    secrets.SystemRandom().shuffle(password)
    
    return ''.join(password)


def hash_password_safely(password: str) -> str:
    """
    Hash password with additional security measures.
    Uses bcrypt (already in use) with additional pepper if available.
    """
    from app.utils.auth import get_password_hash
    
    # Add pepper if available (extra salt layer)
    pepper = os.getenv("PASSWORD_PEPPER", "")
    if pepper:
        # Hash password with pepper before bcrypt
        combined = password + pepper
        hashed_with_pepper = hashlib.sha256(combined.encode()).hexdigest()
        return get_password_hash(hashed_with_pepper)
    
    return get_password_hash(password)


def verify_password_safely(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password with pepper support.
    """
    from app.utils.auth import verify_password
    import os
    
    pepper = os.getenv("PASSWORD_PEPPER", "")
    if pepper:
        # Try with pepper first
        combined = plain_password + pepper
        hashed_with_pepper = hashlib.sha256(combined.encode()).hexdigest()
        if verify_password(hashed_with_pepper, hashed_password):
            return True
    
    # Fall back to standard verification
    return verify_password(plain_password, hashed_password)

