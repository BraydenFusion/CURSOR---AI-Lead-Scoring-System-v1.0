#!/usr/bin/env python3
"""Create users table immediately - works with local or Railway database."""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def create_users_table():
    """Create users table immediately."""
    try:
        from sqlalchemy import create_engine, text, inspect
        
        print("=" * 60)
        print("🚀 Creating Users Table Now")
        print("=" * 60)
        
        # Get database URL - try multiple sources
        database_url = (
            os.getenv("DATABASE_URL") or
            os.getenv("POSTGRES_URL") or
            "postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring"
        )
        
        # Convert postgres:// to postgresql+psycopg://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        
        print(f"🔗 Connecting to database...")
        print(f"   URL: {database_url[:50]}..." if len(database_url) > 50 else f"   URL: {database_url}")
        
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful\n")
        
        # Check if table exists
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'users' in tables:
            print("ℹ️  users table already exists")
            print("\n📋 Current table structure:")
            columns = inspector.get_columns("users")
            for col in columns:
                print(f"   - {col['name']}: {col['type']}")
            
            response = input("\n❓ Do you want to drop and recreate it? (y/N): ")
            if response.lower() != 'y':
                print("✅ Keeping existing table")
                return True
            
            print("\n⚠️  Dropping existing users table...")
            with engine.begin() as conn:
                conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            print("✅ Table dropped")
        
        # Create table
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
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if 'users' in tables:
            columns = inspector.get_columns("users")
            column_names = [col["name"] for col in columns]
            
            print(f"✅ users table created successfully!")
            print(f"\n📊 Table Summary:")
            print(f"   Total columns: {len(column_names)}")
            print(f"   Columns: {', '.join(column_names)}")
            
            # Test insert
            print("\n🧪 Testing table with sample query...")
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                count = result.scalar()
                print(f"   Current user count: {count}")
            
            print("\n" + "=" * 60)
            print("✅ Users table is ready!")
            print("=" * 60)
            
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

