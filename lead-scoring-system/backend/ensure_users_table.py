#!/usr/bin/env python3
"""Ensure users table exists - creates it directly if migrations failed."""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def ensure_users_table():
    """Ensure users table exists, create if missing."""
    try:
        from sqlalchemy import create_engine, text, inspect
        
        print("=" * 60)
        print("🔍 Ensuring Users Table Exists")
        print("=" * 60)
        
        # Get database URL
        database_url = os.getenv("DATABASE_URL", "")
        if not database_url:
            print("❌ ERROR: DATABASE_URL not set")
            return False
        
        # Convert postgres:// to postgresql+psycopg://
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
        
        print(f"🔗 Connecting to database...")
        engine = create_engine(database_url, echo=False)
        
        # Use autocommit connection for DDL operations
        with engine.begin() as conn:
            # Check if users table exists
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'users' in tables:
                print("✅ users table already exists")
                # Verify columns
                columns = inspector.get_columns("users")
                column_names = [col["name"] for col in columns]
                required_cols = ['id', 'email', 'username', 'hashed_password', 'full_name', 'role']
                missing_cols = [col for col in required_cols if col not in column_names]
                if missing_cols:
                    print(f"⚠️  Missing columns: {missing_cols} - will add them")
                else:
                    print(f"   All required columns present ({len(column_names)} total)")
                    return True
            
            print("⚠️  users table does NOT exist - creating it...")
            
            try:
                # Create user_role enum if it doesn't exist
                print("   Step 1: Creating user_role enum...")
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE user_role AS ENUM ('admin', 'manager', 'sales_rep');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                print("   ✅ user_role enum created/verified")
                
                # Create users table
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
                
                # Create indexes
                print("   Step 3: Creating indexes...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_username ON users(username)
                """))
                print("   ✅ indexes created")
                
                # Verify table was created
                inspector = inspect(engine)
                tables = inspector.get_table_names()
                
                if 'users' in tables:
                    print("\n✅ users table created successfully!")
                    
                    # Check columns
                    columns = inspector.get_columns("users")
                    column_names = [col["name"] for col in columns]
                    print(f"   Total columns: {len(column_names)}")
                    print(f"   Column names: {', '.join(column_names)}")
                    
                    required_cols = ['id', 'email', 'username', 'hashed_password', 'full_name', 'role']
                    missing_cols = [col for col in required_cols if col not in column_names]
                    if missing_cols:
                        print(f"   ⚠️  Missing required columns: {missing_cols}")
                        return False
                    else:
                        print(f"   ✅ All required columns present")
                        return True
                else:
                    print("\n❌ ERROR: Table creation failed - users table still doesn't exist")
                    return False
                    
            except Exception as e:
                print(f"\n❌ Error creating users table: {e}")
                import traceback
                traceback.print_exc()
                # Try to rollback if possible
                try:
                    conn.rollback()
                except:
                    pass
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ensure_users_table()
    sys.exit(0 if success else 1)

