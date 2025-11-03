#!/usr/bin/env python3
"""Create admin user with high security password.

Usage:
    python create_admin_user.py
    # Or with custom credentials:
    python create_admin_user.py --username admin --password "YourSecurePass123!"
"""

import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash
from app.utils.password_security import validate_password_strength, check_password_breach

def create_admin_user(username: str = "admin", password: str = "Admin123!@#Secure", email: str = "admin@example.com", full_name: str = "Admin User"):
    """Create admin user in database."""
    
    # High security: Validate password
    if password:
        is_valid, error_msg = validate_password_strength(password)
        if not is_valid:
            print(f"❌ Password validation failed: {error_msg}")
            print("\nPassword requirements:")
            print("  - At least 12 characters")
            print("  - At least one uppercase letter")
            print("  - At least one lowercase letter")
            print("  - At least one number")
            print("  - At least one special character")
            print("  - No common words or patterns")
            return False
        
        if check_password_breach(password):
            print("❌ Password has been found in data breaches. Please choose a different password.")
            return False
    
    # Create database session
    db = next(get_db())
    
    try:
        # Check if admin already exists
        existing = db.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if existing:
            print(f"⚠️  User '{username}' or email '{email}' already exists.")
            response = input("Do you want to update the password? (yes/no): ")
            if response.lower() == 'yes':
                hashed = get_password_hash(password)
                existing.hashed_password = hashed
                existing.is_active = True
                db.commit()
                print(f"✅ Password updated for user '{username}'")
                return True
            else:
                print("Cancelled.")
                return False
        
        # Create new admin user
        hashed_password = get_password_hash(password)
        admin_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=UserRole.ADMIN,
            is_active=True,
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print("=" * 60)
        print("✅ Admin user created successfully!")
        print("=" * 60)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Role: ADMIN")
        print(f"Password: [hidden]")
        print("=" * 60)
        print("\n⚠️  SECURITY REMINDER:")
        print("   - Change this password after first login")
        print("   - Use a strong, unique password")
        print("   - Never share credentials")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create admin user")
    parser.add_argument("--username", default="admin", help="Admin username (default: admin)")
    parser.add_argument("--password", default="Admin123!@#Secure", help="Admin password (default: Admin123!@#Secure)")
    parser.add_argument("--email", default="admin@example.com", help="Admin email (default: admin@example.com)")
    parser.add_argument("--full-name", default="Admin User", help="Admin full name (default: Admin User)")
    
    args = parser.parse_args()
    
    # For backward compatibility, allow admin123 if specified
    if args.password == "admin123":
        print("⚠️  WARNING: 'admin123' is too weak. Using default secure password.")
        print("   Login with: admin / Admin123!@#Secure")
        args.password = "Admin123!@#Secure"
    
    success = create_admin_user(
        username=args.username,
        password=args.password,
        email=args.email,
        full_name=args.full_name
    )
    
    sys.exit(0 if success else 1)

