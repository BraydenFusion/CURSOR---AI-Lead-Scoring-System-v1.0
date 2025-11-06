"""Script to ensure onboarding fields exist in users table.
This script directly adds the columns if they don't exist, bypassing migrations.
"""

import sys
from sqlalchemy import text, inspect
from app.database import engine
from app.config import get_settings

def ensure_onboarding_fields():
    """Ensure onboarding fields exist in users table."""
    settings = get_settings()
    print("=" * 60)
    print("🔍 Ensuring Onboarding Fields in Users Table")
    print("=" * 60)
    print(f"🔗 Connecting to database...")
    print()
    
    try:
        with engine.connect() as conn:
            inspector = inspect(engine)
            
            # Check if users table exists
            tables = inspector.get_table_names()
            if 'users' not in tables:
                print("❌ ERROR: users table does not exist!")
                print("⚠️  Run migrations or create_users_table script first.")
                return False
            
            print("✅ users table exists")
            print()
            
            # Get current columns
            columns = {col['name']: col for col in inspector.get_columns('users')}
            print(f"📋 Current columns: {len(columns)}")
            print()
            
            # Check and add company_name
            if 'company_name' not in columns:
                print("   ➕ Adding company_name column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN company_name VARCHAR(255) NULL
                """))
                conn.commit()
                print("   ✅ company_name column added")
            else:
                print("   ✅ company_name column already exists")
            
            # Check and add payment_plan
            if 'payment_plan' not in columns:
                print("   ➕ Adding payment_plan column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN payment_plan VARCHAR(50) NULL
                """))
                conn.commit()
                print("   ✅ payment_plan column added")
            else:
                print("   ✅ payment_plan column already exists")
            
            # Check and add onboarding_completed
            if 'onboarding_completed' not in columns:
                print("   ➕ Adding onboarding_completed column...")
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN onboarding_completed BOOLEAN NOT NULL DEFAULT false
                """))
                conn.commit()
                print("   ✅ onboarding_completed column added")
            else:
                print("   ✅ onboarding_completed column already exists")
            
            print()
            print("✅ All onboarding fields verified/added successfully!")
            print()
            
            # Verify final state
            inspector = inspect(engine)
            final_columns = {col['name']: col for col in inspector.get_columns('users')}
            print("📊 Final table structure:")
            print(f"   Total columns: {len(final_columns)}")
            print(f"   ✅ company_name: {'exists' if 'company_name' in final_columns else 'MISSING'}")
            print(f"   ✅ payment_plan: {'exists' if 'payment_plan' in final_columns else 'MISSING'}")
            print(f"   ✅ onboarding_completed: {'exists' if 'onboarding_completed' in final_columns else 'MISSING'}")
            
            return True
            
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = ensure_onboarding_fields()
    sys.exit(0 if success else 1)

