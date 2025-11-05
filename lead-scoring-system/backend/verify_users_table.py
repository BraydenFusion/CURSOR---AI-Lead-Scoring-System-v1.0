#!/usr/bin/env python3
"""Verify that the users table exists and has the correct structure."""

import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.engine import Engine

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

def verify_users_table(engine: Engine):
    """Verify users table structure."""
    inspector = inspect(engine)
    
    print("=" * 60)
    print("🔍 Verifying Users Table")
    print("=" * 60)
    
    # Check if table exists
    tables = inspector.get_table_names()
    if "users" not in tables:
        print("❌ ERROR: 'users' table does NOT exist!")
        print("\nSOLUTION:")
        print("Run database migrations:")
        print("  alembic upgrade head")
        print("\nOr manually create the table using:")
        print("  psql <DATABASE_URL> -f create_users_table.sql")
        return False
    
    print("✅ 'users' table exists")
    
    # Get table columns
    columns = inspector.get_columns("users")
    column_names = [col["name"] for col in columns]
    
    print(f"\n📋 Table Structure ({len(columns)} columns):")
    print("-" * 60)
    
    # Required columns
    required_columns = [
        "id", "email", "username", "hashed_password", "full_name",
        "role", "is_active", "created_at", "updated_at"
    ]
    
    # Optional columns
    optional_columns = ["last_login", "profile_picture_url", "company_role"]
    
    all_columns = required_columns + optional_columns
    
    for col in columns:
        col_name = col["name"]
        col_type = str(col["type"])
        nullable = "NULL" if col["nullable"] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col.get("default") else ""
        
        status = "✅" if col_name in all_columns else "⚠️"
        print(f"{status} {col_name:25} {col_type:30} {nullable}{default}")
    
    # Check for required columns
    missing_required = [col for col in required_columns if col not in column_names]
    if missing_required:
        print(f"\n❌ Missing required columns: {', '.join(missing_required)}")
        return False
    
    # Check for optional columns
    missing_optional = [col for col in optional_columns if col not in column_names]
    if missing_optional:
        print(f"\n⚠️  Missing optional columns: {', '.join(missing_optional)}")
        print("   These can be added via migrations:")
        print("   - 004_add_profile_picture.py (profile_picture_url)")
        print("   - 005_add_company_role.py (company_role)")
    
    # Check indexes
    print("\n📊 Indexes:")
    indexes = inspector.get_indexes("users")
    for idx in indexes:
        print(f"   ✅ {idx['name']}: {', '.join(idx['column_names'])}")
    
    # Check enum type
    print("\n🔍 Checking user_role enum type...")
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM pg_type WHERE typname = 'user_role'
            )
        """))
        enum_exists = result.scalar()
        if enum_exists:
            print("   ✅ user_role enum type exists")
        else:
            print("   ⚠️  user_role enum type not found (may need migration)")
    
    # Count users
    print("\n📈 Current Data:")
    with engine.connect() as conn:
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        user_count = result.scalar()
        print(f"   Total users: {user_count}")
        
        if user_count > 0:
            result = conn.execute(text("""
                SELECT role, COUNT(*) as count 
                FROM users 
                GROUP BY role
            """))
            print("\n   Users by role:")
            for row in result:
                print(f"     - {row[0]}: {row[1]}")
    
    print("\n" + "=" * 60)
    print("✅ Users table verification complete!")
    print("=" * 60)
    
    return True

def main():
    """Main function."""
    try:
        database_url = get_database_url()
        print(f"🔗 Connecting to database...")
        print(f"   URL: {database_url[:50]}..." if len(database_url) > 50 else f"   URL: {database_url}")
        
        engine = create_engine(database_url, echo=False)
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        print("✅ Database connection successful\n")
        
        # Verify table
        success = verify_users_table(engine)
        
        if success:
            print("\n✅ All checks passed! Users table is ready.")
            sys.exit(0)
        else:
            print("\n❌ Some checks failed. Please run migrations:")
            print("   alembic upgrade head")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTroubleshooting:")
        print("1. Check DATABASE_URL environment variable")
        print("2. Verify database is accessible")
        print("3. Check database connection credentials")
        sys.exit(1)

if __name__ == "__main__":
    main()

