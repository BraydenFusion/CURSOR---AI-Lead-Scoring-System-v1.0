#!/usr/bin/env python3
"""Create sales rep user account.

Usage:
    python create_sales_rep_user.py
    # Or with custom credentials:
    python create_sales_rep_user.py --username brayden --email brayden@example.com --password "YourSecurePass123!"
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

def create_sales_rep_user(
    username: str = "brayden",
    password: str = "BraydenSecure123!@",
    email: str = "bsaundersjones@gmail.com",
    full_name: str = "Brayden Saunders-Jones",
    company_role: str = "VP Sales"
):
    """Create sales rep user in database."""
    
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
        # Check if user already exists
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
                existing.role = UserRole.SALES_REP.value  # Ensure correct role
                db.commit()
                print(f"✅ Password updated for user '{username}'")
                print(f"✅ Role set to: SALES_REP")
                return True
            else:
                print("Cancelled.")
                return False
        
        # Create new sales rep user
        # CRITICAL: Use enum value (lowercase string) for role
        hashed_password = get_password_hash(password)
        sales_rep_user = User(
            username=username,
            email=email,
            full_name=full_name,
            hashed_password=hashed_password,
            role=UserRole.SALES_REP.value,  # Must be "sales_rep" (lowercase string)
            company_role=company_role,
            is_active=True,
            onboarding_completed=True,  # Skip onboarding for manually created accounts
        )
        
        db.add(sales_rep_user)
        db.commit()
        db.refresh(sales_rep_user)
        
        print("=" * 70)
        print("✅ Sales Rep user created successfully!")
        print("=" * 70)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Full Name: {full_name}")
        print(f"Company Role: {company_role}")
        print(f"Role: SALES_REP")
        print(f"Password: {password}")
        print("=" * 70)
        print("\n📍 LOGIN CREDENTIALS:")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        print("=" * 70)
        print("\n⚠️  SECURITY REMINDER:")
        print("   - Change this password after first login")
        print("   - Use a strong, unique password")
        print("   - Never share credentials")
        print("   - You can access your dashboard at: /dashboard/sales-rep")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating sales rep user: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        return False
    finally:
        db.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create sales rep user account")
    parser.add_argument("--username", default="brayden", help="Username (default: brayden)")
    parser.add_argument("--password", default="BraydenSecure123!@", help="Password (default: BraydenSecure123!@)")
    parser.add_argument("--email", default="bsaundersjones@gmail.com", help="Email (default: bsaundersjones@gmail.com)")
    parser.add_argument("--full-name", default="Brayden Saunders-Jones", help="Full name (default: Brayden Saunders-Jones)")
    parser.add_argument("--company-role", default="VP Sales", help="Company role (default: VP Sales)")
    
    args = parser.parse_args()
    
    success = create_sales_rep_user(
        username=args.username,
        password=args.password,
        email=args.email,
        full_name=args.full_name,
        company_role=args.company_role
    )
    
    sys.exit(0 if success else 1)

