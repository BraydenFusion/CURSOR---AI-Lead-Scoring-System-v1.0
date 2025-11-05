#!/usr/bin/env python3
"""Run database migrations programmatically - more reliable than shell script."""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def run_migrations():
    """Run Alembic migrations."""
    try:
        from alembic import command
        from alembic.config import Config
        
        print("=" * 60)
        print("🔄 Running Database Migrations")
        print("=" * 60)
        
        # Get alembic.ini path
        alembic_ini = backend_dir / "alembic.ini"
        if not alembic_ini.exists():
            print(f"❌ ERROR: alembic.ini not found at {alembic_ini}")
            return False
        
        print(f"📄 Using alembic.ini: {alembic_ini}")
        
        # Create Alembic config
        alembic_cfg = Config(str(alembic_ini))
        
        # Check current revision
        try:
            from alembic.script import ScriptDirectory
            from alembic.runtime.migration import MigrationContext
            from sqlalchemy import create_engine, text
            
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
            # Ensure we're using psycopg3 (not psycopg2)
            # SQLAlchemy 2.0 supports postgresql+psycopg:// for psycopg3
            if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
                database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
            engine = create_engine(database_url, echo=False)
            
            # Check current revision
            with engine.connect() as conn:
                context = MigrationContext.configure(conn)
                current_rev = context.get_current_revision()
                print(f"📍 Current database revision: {current_rev or 'none (uninitialized)'}")
            
            # Run migrations
            print("\n🚀 Running migrations to head...")
            command.upgrade(alembic_cfg, "head")
            
            print("\n✅ Migrations completed successfully!")
            
            # Verify tables exist
            print("\n🔍 Verifying tables...")
            with engine.connect() as conn:
                result = conn.execute(text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name IN ('users', 'leads', 'lead_activities')
                    ORDER BY table_name
                """))
                tables = [row[0] for row in result]
                
                if 'users' in tables:
                    print("   ✅ users table exists")
                else:
                    print("   ❌ users table missing!")
                    return False
                
                if 'leads' in tables:
                    print("   ✅ leads table exists")
                else:
                    print("   ⚠️  leads table missing")
                
                if 'lead_activities' in tables:
                    print("   ✅ lead_activities table exists")
                else:
                    print("   ⚠️  lead_activities table missing")
            
            print("\n" + "=" * 60)
            print("✅ Database migration verification complete!")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Migration error: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    except ImportError as e:
        print(f"❌ ERROR: Could not import Alembic: {e}")
        print("\nMake sure alembic is installed:")
        print("  pip install alembic")
        return False
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_migrations()
    sys.exit(0 if success else 1)

