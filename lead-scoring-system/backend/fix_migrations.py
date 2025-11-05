#!/usr/bin/env python3
"""Fix migration issues by stamping database to correct revision and running migrations."""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def fix_migrations():
    """Fix migration state and run migrations."""
    try:
        from alembic import command
        from alembic.config import Config
        from sqlalchemy import create_engine, text, inspect
        
        print("=" * 60)
        print("🔧 Fixing Database Migrations")
        print("=" * 60)
        
        # Get database URL
        try:
            from app.config import get_settings
            settings = get_settings()
            database_url = settings.database_url
        except Exception:
            database_url = os.getenv("DATABASE_URL", "")
            if not database_url:
                print("❌ ERROR: DATABASE_URL not set")
                return False
            if database_url.startswith("postgres://"):
                database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
            if database_url.startswith("postgresql://") and "+psycopg" not in database_url:
                database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)
        
        print(f"🔗 Connecting to database...")
        engine = create_engine(database_url, echo=False)
        
        # Check current state
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            print(f"\n📊 Current database state:")
            print(f"   Tables: {', '.join(tables) if tables else 'none'}")
            
            # Check alembic_version
            if 'alembic_version' in tables:
                result = conn.execute(text("SELECT version_num FROM alembic_version"))
                current_rev = result.scalar()
                print(f"   Current migration revision: {current_rev or 'none'}")
            else:
                print(f"   ⚠️  alembic_version table doesn't exist")
        
        # Get alembic config
        alembic_ini = backend_dir / "alembic.ini"
        if not alembic_ini.exists():
            print(f"❌ ERROR: alembic.ini not found at {alembic_ini}")
            return False
        
        alembic_cfg = Config(str(alembic_ini))
        
        # Strategy: If no tables exist except alembic_version, stamp to 000_initial
        if 'leads' not in tables and 'users' not in tables:
            print("\n⚠️  Base tables (leads, users) don't exist")
            print("   Stamping database to 000_initial...")
            try:
                command.stamp(alembic_cfg, "000_initial")
                print("   ✅ Stamped to 000_initial")
            except Exception as e:
                print(f"   ⚠️  Stamping failed: {e}")
        
        # Run migrations
        print("\n🚀 Running migrations...")
        try:
            command.upgrade(alembic_cfg, "head")
            print("✅ Migrations completed")
        except Exception as e:
            print(f"❌ Migration error: {e}")
            print("\n⚠️  Migrations failed - will try direct table creation...")
            return False
        
        # Verify tables
        print("\n🔍 Verifying tables...")
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            required_tables = ['users', 'leads']
            missing = [t for t in required_tables if t not in tables]
            
            if missing:
                print(f"❌ Missing tables: {', '.join(missing)}")
                return False
            else:
                print(f"✅ All required tables exist: {', '.join(required_tables)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = fix_migrations()
    sys.exit(0 if success else 1)

