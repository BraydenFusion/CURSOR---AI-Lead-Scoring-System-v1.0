#!/usr/bin/env python3
"""Add missing columns to users table if they don't exist."""

import os
import sys

try:
    from sqlalchemy import create_engine, text
except ImportError:
    print("❌ Error: sqlalchemy is not installed")
    print("\nSOLUTION:")
    print("1. Activate your virtual environment:")
    print("   source venv/bin/activate")
    print("\n2. Install dependencies:")
    print("   pip install -r requirements.txt")
    sys.exit(1)

def get_database_url():
    """Get database URL from environment."""
    url = (
        os.getenv("DATABASE_URL") or
        os.getenv("POSTGRES_URL") or
        "postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring"
    )
    
    # Convert Railway postgres:// to postgresql+psycopg://
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+psycopg://", 1)
    
    return url

def add_missing_columns():
    """Add missing columns to users table."""
    database_url = get_database_url()
    
    print("=" * 60)
    print("🔧 Adding Missing Columns to Users Table")
    print("=" * 60)
    
    try:
        engine = create_engine(database_url, echo=False)
        
        with engine.connect() as conn:
            # Start transaction
            trans = conn.begin()
            
            try:
                # Check if profile_picture_url exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'profile_picture_url'
                """))
                
                if not result.fetchone():
                    print("➕ Adding profile_picture_url column...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN profile_picture_url VARCHAR(500) NULL
                    """))
                    print("   ✅ profile_picture_url added")
                else:
                    print("   ✅ profile_picture_url already exists")
                
                # Check if company_role exists
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name = 'company_role'
                """))
                
                if not result.fetchone():
                    print("➕ Adding company_role column...")
                    conn.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN company_role VARCHAR(100) NULL
                    """))
                    print("   ✅ company_role added")
                else:
                    print("   ✅ company_role already exists")
                
                # Commit transaction
                trans.commit()
                
                print("\n" + "=" * 60)
                print("✅ All columns added successfully!")
                print("=" * 60)
                
                # Verify
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' 
                    AND column_name IN ('profile_picture_url', 'company_role')
                    ORDER BY column_name
                """))
                
                columns = [row[0] for row in result]
                print(f"\n📋 Verified columns: {', '.join(columns) if columns else 'None found'}")
                
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"\n❌ Error adding columns: {e}")
                return False
                
    except Exception as e:
        print(f"\n❌ Database connection error: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL environment variable")
        print("2. Verify database is accessible")
        print("3. Check database connection credentials")
        return False

if __name__ == "__main__":
    success = add_missing_columns()
    sys.exit(0 if success else 1)

