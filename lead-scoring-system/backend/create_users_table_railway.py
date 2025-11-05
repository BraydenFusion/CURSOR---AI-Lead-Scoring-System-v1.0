#!/usr/bin/env python3
"""Create users table on Railway - Run this from Railway Shell or CLI."""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def create_users_table():
    """Create users table directly using SQL."""
    try:
        from sqlalchemy import create_engine, text
        
        print("=" * 60)
        print("🚀 Creating Users Table on Railway")
        print("=" * 60)
        
        # Get database URL from app config (handles Railway format)
        try:
            from app.config import get_settings
            settings = get_settings()
            database_url = settings.database_url
        except Exception as e:
            # Fallback to environment variable
            database_url = os.getenv("DATABASE_URL", "")
            if not database_url:
                print("❌ ERROR: DATABASE_URL not set")
                print("\nThis script needs DATABASE_URL environment variable.")
                print("On Railway, this should be set automatically.")
                return False
            # Convert postgres:// to postgresql+psycopg:// (for psycopg3)
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
            if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
                database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
        print(f"🔗 Connecting to database...")
        engine = create_engine(database_url, echo=False)
        
        # Check if table exists
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                print("✅ users table already exists!")
                
                # Show table structure
                result = conn.execute(text("""
                    SELECT column_name, data_type, is_nullable
                    FROM information_schema.columns
                    WHERE table_name = 'users'
                    ORDER BY ordinal_position
                """))
                
                print("\n📋 Current table structure:")
                for row in result:
                    nullable = "NULL" if row[2] == "YES" else "NOT NULL"
                    print(f"   - {row[0]}: {row[1]} ({nullable})")
                
                response = input("\n❓ Do you want to drop and recreate it? (y/N): ")
                if response.lower() != 'y':
                    print("✅ Keeping existing table")
                    return True
                
                print("\n⚠️  Dropping existing users table...")
                conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
                conn.commit()
                print("✅ Table dropped")
        
        # Create table using SQL
        print("\n🔨 Creating users table...")
        
        with engine.begin() as conn:
            # Step 1: Create enum type
            print("   Step 1: Creating user_role enum...")
            conn.execute(text("""
                DO $$ BEGIN
                    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'sales_rep');
                EXCEPTION
                    WHEN duplicate_object THEN null;
                END $$;
            """))
            print("   ✅ user_role enum created")
            
            # Step 2: Create users table
            print("   Step 2: Creating users table...")
            conn.execute(text("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                    email VARCHAR(255) NOT NULL UNIQUE,
                    username VARCHAR(100) NOT NULL UNIQUE,
                    hashed_password VARCHAR(255) NOT NULL,
                    full_name VARCHAR(255) NOT NULL,
                    role user_role NOT NULL DEFAULT 'sales_rep',
                    is_active BOOLEAN NOT NULL DEFAULT true,
                    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                    last_login TIMESTAMP NULL,
                    profile_picture_url VARCHAR(500) NULL,
                    company_role VARCHAR(100) NULL
                )
            """))
            print("   ✅ users table created")
            
            # Step 3: Create indexes
            print("   Step 3: Creating indexes...")
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)
            """))
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_username ON users(username)
            """))
            print("   ✅ indexes created")
        
        # Verify
        print("\n🔍 Verifying table creation...")
        with engine.connect() as conn:
            result = conn.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = 'users'
                )
            """))
            table_exists = result.scalar()
            
            if table_exists:
                # Count columns
                result = conn.execute(text("""
                    SELECT COUNT(*) 
                    FROM information_schema.columns 
                    WHERE table_name = 'users'
                """))
                column_count = result.scalar()
                
                # Count users
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                
                print(f"✅ users table created successfully!")
                print(f"\n📊 Table Summary:")
                print(f"   Total columns: {column_count}")
                print(f"   Current users: {user_count}")
                
                print("\n" + "=" * 60)
                print("✅ SUCCESS! Users table is ready!")
                print("=" * 60)
                print("\nYou can now:")
                print("  ✅ Register new users")
                print("  ✅ Login with existing users")
                print("  ✅ Create admin users via API")
                
                return True
            else:
                print("❌ ERROR: Table creation failed")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_users_table()
    sys.exit(0 if success else 1)

