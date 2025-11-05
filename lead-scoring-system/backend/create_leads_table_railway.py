#!/usr/bin/env python3
"""
Script to create the leads table directly on Railway,
to be run via Railway Shell or CLI.
This creates the leads table with all required columns.
"""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def create_leads_table_railway():
    """Create leads table and required enums if they don't exist."""
    try:
        from sqlalchemy import create_engine, text, inspect
        
        print("=" * 60)
        print("🚀 Creating Leads Table Now")
        print("=" * 60)
        
        # Get database URL from app config (handles conversion properly)
        try:
            from app.config import get_settings
            settings = get_settings()
            database_url = settings.database_url
        except Exception:
            # Fallback to environment variable
            database_url = os.getenv("DATABASE_URL", "")
            if not database_url:
                print("❌ ERROR: DATABASE_URL not set")
                return False
            # Convert postgres:// to postgresql+psycopg:// (for psycopg3)
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
            # Ensure psycopg driver is specified
            if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
                database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
        print(f"🔗 Connecting to database...")
        engine = create_engine(database_url, echo=False)
        
        # Use autocommit connection for DDL operations
        with engine.begin() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'leads' in tables:
                print("ℹ️  leads table already exists")
                response = input("❓ Do you want to drop and recreate it? (y/N): ").lower()
                if response == 'y':
                    print("⚠️  Dropping existing leads table...")
                    conn.execute(text("DROP TABLE IF EXISTS leads CASCADE"))
                    print("✅ Existing table dropped.")
                else:
                    print("✅ Keeping existing table")
                    # Verify current structure
                    print("\n📋 Current table structure:")
                    columns = inspector.get_columns("leads")
                    for col in columns:
                        print(f"   - {col['name']}: {col['type']}")
                    return True # Exit if not recreating
            
            print("⚠️  leads table does NOT exist or is being recreated - proceeding with creation...")
            
            try:
                # Step 1: Create lead_classification enum if it doesn't exist
                print("   Step 1: Creating lead_classification enum...")
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE lead_classification AS ENUM ('hot', 'warm', 'cold');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                print("   ✅ lead_classification enum created/verified")
                
                # Step 2: Create lead_status enum if it doesn't exist
                print("   Step 2: Creating lead_status enum...")
                conn.execute(text("""
                    DO $$ BEGIN
                        CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'won', 'lost');
                    EXCEPTION
                        WHEN duplicate_object THEN null;
                    END $$;
                """))
                print("   ✅ lead_status enum created/verified")
                
                # Step 3: Create leads table
                print("   Step 3: Creating leads table...")
                conn.execute(text("""
                    CREATE TABLE leads (
                        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                        name VARCHAR(255) NOT NULL,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        phone VARCHAR(50) NULL,
                        source VARCHAR(100) NOT NULL,
                        location VARCHAR(255) NULL,
                        current_score INTEGER NOT NULL DEFAULT 0 CHECK (current_score >= 0 AND current_score <= 100),
                        classification lead_classification NULL,
                        status lead_status NOT NULL DEFAULT 'new',
                        contacted_at TIMESTAMP NULL,
                        qualified_at TIMESTAMP NULL,
                        closed_at TIMESTAMP NULL,
                        created_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
                        metadata JSONB NOT NULL DEFAULT '{}',
                        created_by UUID NULL REFERENCES users(id) ON DELETE SET NULL
                    )
                """))
                print("   ✅ leads table created")
                
                # Step 4: Create indexes
                print("   Step 4: Creating indexes...")
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_leads_email ON leads(email)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_leads_status ON leads(status)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_leads_classification ON leads(classification)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_leads_current_score ON leads(current_score)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_leads_created_at ON leads(created_at)
                """))
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS idx_leads_created_by ON leads(created_by)
                """))
                print("   ✅ indexes created")
                
                # Final verification
                inspector = inspect(engine)
                if 'leads' in inspector.get_table_names():
                    print("\n✅ leads table created successfully!")
                    columns = inspector.get_columns("leads")
                    print(f"   Total columns: {len(columns)}")
                    print(f"   Column names: {', '.join([col['name'] for col in columns])}")
                    
                    # Verify required columns
                    column_names = [col['name'] for col in columns]
                    required_cols = ['id', 'name', 'email', 'source', 'current_score', 'status', 'created_at', 'updated_at', 'metadata']
                    missing_cols = [col for col in required_cols if col not in column_names]
                    if missing_cols:
                        print(f"   ⚠️  Missing required columns: {missing_cols}")
                        return False
                    else:
                        print(f"   ✅ All required columns present")
                        return True
                else:
                    print("\n❌ ERROR: Table creation failed - leads table still doesn't exist")
                    return False
                    
            except Exception as e:
                print(f"\n❌ Error during table creation: {e}")
                import traceback
                traceback.print_exc()
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = create_leads_table_railway()
    sys.exit(0 if success else 1)

