#!/usr/bin/env python3
"""Create Brayden's account directly in the Railway database.

This script connects directly to the database and creates the user account.
It can be run on Railway via Railway CLI or shell.

Usage on Railway:
    railway run python create_brayden_account_railway.py

Or locally (with DATABASE_URL set):
    DATABASE_URL=postgresql://... python create_brayden_account_railway.py
"""

import os
import sys
from uuid import uuid4
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine, text
from app.utils.auth import get_password_hash

# Account credentials
USERNAME = "brayden"
EMAIL = "bsaundersjones@gmail.com"
PASSWORD = "Brayden@Secure2024!"
FULL_NAME = "Brayden Saunders-Jones"
COMPANY_ROLE = "VP Sales"
ROLE = "sales_rep"  # Must be lowercase to match database enum
PAYMENT_PLAN = "free"
ONBOARDING_COMPLETED = True

def create_brayden_account():
    """Create Brayden's account directly in the database."""
    
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not set")
        print("\n💡 To run this script:")
        print("   1. On Railway: railway run python create_brayden_account_railway.py")
        print("   2. Locally: Set DATABASE_URL=postgresql://...")
        return False
    
    # Convert postgres:// to postgresql+psycopg:// if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    print("=" * 70)
    print("🚀 Creating Brayden's Sales Rep Account")
    print("=" * 70)
    print(f"Username: {USERNAME}")
    print(f"Email: {EMAIL}")
    print(f"Role: {ROLE}")
    print(f"Payment Plan: {PAYMENT_PLAN}")
    print("=" * 70)
    print("\n🔗 Connecting to database...")
    
    try:
        # Create database connection
        engine = create_engine(database_url, echo=False)
        
        with engine.begin() as conn:
            # Check if user already exists
            check_query = text("""
                SELECT id, username, email, role 
                FROM users 
                WHERE username = :username OR email = :email
            """)
            result = conn.execute(check_query, {"username": USERNAME, "email": EMAIL})
            existing = result.fetchone()
            
            if existing:
                print(f"\n⚠️  User already exists!")
                print(f"   ID: {existing[0]}")
                print(f"   Username: {existing[1]}")
                print(f"   Email: {existing[2]}")
                print(f"   Role: {existing[3]}")
                
                # Update password and ensure correct role/plan
                print("\n🔄 Updating password and account settings...")
                hashed_password = get_password_hash(PASSWORD)
                
                update_query = text("""
                    UPDATE users 
                    SET hashed_password = :hashed_password,
                        role = :role,
                        payment_plan = :payment_plan,
                        company_role = :company_role,
                        onboarding_completed = :onboarding_completed,
                        is_active = true,
                        updated_at = :updated_at
                    WHERE username = :username OR email = :email
                """)
                
                conn.execute(update_query, {
                    "hashed_password": hashed_password,
                    "role": ROLE,  # Lowercase "sales_rep"
                    "payment_plan": PAYMENT_PLAN,
                    "company_role": COMPANY_ROLE,
                    "onboarding_completed": ONBOARDING_COMPLETED,
                    "updated_at": datetime.utcnow(),
                    "username": USERNAME,
                    "email": EMAIL
                })
                
                print("✅ Account updated successfully!")
            else:
                # Create new user
                print("\n📝 Creating new user account...")
                
                # Hash password
                hashed_password = get_password_hash(PASSWORD)
                user_id = uuid4()
                now = datetime.utcnow()
                
                # Insert user with all required fields
                insert_query = text("""
                    INSERT INTO users (
                        id, email, username, hashed_password, full_name, 
                        role, is_active, created_at, updated_at, 
                        company_role, payment_plan, onboarding_completed
                    ) VALUES (
                        :id, :email, :username, :hashed_password, :full_name,
                        :role, :is_active, :created_at, :updated_at,
                        :company_role, :payment_plan, :onboarding_completed
                    )
                """)
                
                conn.execute(insert_query, {
                    "id": user_id,
                    "email": EMAIL,
                    "username": USERNAME,
                    "hashed_password": hashed_password,
                    "full_name": FULL_NAME,
                    "role": ROLE,  # CRITICAL: Must be lowercase "sales_rep" not "SALES_REP"
                    "is_active": True,
                    "created_at": now,
                    "updated_at": now,
                    "company_role": COMPANY_ROLE,
                    "payment_plan": PAYMENT_PLAN,
                    "onboarding_completed": ONBOARDING_COMPLETED
                })
                
                print("✅ Account created successfully!")
                print(f"   User ID: {user_id}")
        
        print("\n" + "=" * 70)
        print("✅ ACCOUNT READY!")
        print("=" * 70)
        print("\n📍 YOUR LOGIN CREDENTIALS:")
        print(f"   Username: {USERNAME}")
        print(f"   Password: {PASSWORD}")
        print(f"   Email: {EMAIL}")
        print("\n🌐 LOGIN URLS:")
        print("   https://ventrix.tech/login")
        print("   https://frontend-production-e9b2.up.railway.app/login")
        print("\n📊 Dashboard:")
        print("   /dashboard/sales-rep")
        print("\n💳 Payment Plan:")
        print(f"   {PAYMENT_PLAN.upper()} (Individual)")
        print("=" * 70)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error creating account: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_brayden_account()
    sys.exit(0 if success else 1)

