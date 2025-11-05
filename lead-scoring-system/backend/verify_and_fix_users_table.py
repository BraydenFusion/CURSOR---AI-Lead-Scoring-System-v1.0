#!/usr/bin/env python3
"""Verify and fix users table structure to ensure sign in/sign up works."""

import os
import sys
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(backend_dir))

def verify_and_fix_users_table():
    """Verify users table structure and fix any issues."""
    try:
        from sqlalchemy import create_engine, text, inspect
        
        print("=" * 60)
        print("🔍 Verifying and Fixing Users Table")
        print("=" * 60)
        
        # Get database URL
        try:
            from app.config import get_settings
            settings = get_settings()
            database_url = settings.database_url
        except Exception as e:
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
        
        with engine.connect() as conn:
            inspector = inspect(engine)
            tables = inspector.get_table_names()
            
            if 'users' not in tables:
                print("❌ ERROR: users table does not exist!")
                print("\nPlease create the users table first via Railway UI.")
                return False
            
            print("✅ users table exists")
            
            # Get current columns
            columns = inspector.get_columns("users")
            column_names = [col["name"] for col in columns]
            column_dict = {col["name"]: col for col in columns}
            
            print(f"\n📋 Current table structure ({len(columns)} columns):")
            for col in columns:
                col_type = str(col["type"])
                nullable = "NULL" if col["nullable"] else "NOT NULL"
                default = f" DEFAULT {col['default']}" if col.get("default") else ""
                print(f"   - {col['name']}: {col_type} ({nullable}){default}")
            
            # Required columns for sign in/sign up
            required_columns = {
                'id': {'type': 'uuid', 'nullable': False, 'has_default': True},
                'email': {'type': 'varchar', 'nullable': False, 'unique': True},
                'username': {'type': 'varchar', 'nullable': False, 'unique': True},
                'hashed_password': {'type': 'varchar', 'nullable': False},
                'full_name': {'type': 'varchar', 'nullable': False},
                'role': {'type': 'varchar', 'nullable': False, 'has_default': True},
                'is_active': {'type': 'boolean', 'nullable': False, 'has_default': True},
                'created_at': {'type': 'timestamp', 'nullable': False, 'has_default': True},
                'updated_at': {'type': 'timestamp', 'nullable': False, 'has_default': True},
            }
            
            # Optional columns
            optional_columns = {
                'last_login': {'type': 'timestamp', 'nullable': True},
                'profile_picture_url': {'type': 'varchar', 'nullable': True},
                'company_role': {'type': 'varchar', 'nullable': True},
            }
            
            print("\n🔍 Checking required columns...")
            missing_required = []
            issues_found = []
            
            for col_name, col_spec in required_columns.items():
                if col_name not in column_names:
                    missing_required.append(col_name)
                    print(f"   ❌ Missing: {col_name}")
                else:
                    col_info = column_dict[col_name]
                    # Check if nullable matches
                    if col_spec['nullable'] and not col_info['nullable']:
                        issues_found.append(f"{col_name}: should be nullable")
                    elif not col_spec['nullable'] and col_info['nullable']:
                        issues_found.append(f"{col_name}: should NOT be nullable")
                    print(f"   ✅ {col_name}: exists")
            
            # Check optional columns
            missing_optional = []
            for col_name, col_spec in optional_columns.items():
                if col_name not in column_names:
                    missing_optional.append(col_name)
                    print(f"   ⚠️  Missing optional: {col_name}")
            
            # Fix issues
            if missing_required or issues_found or missing_optional:
                print("\n🔧 Fixing issues...")
                
                with engine.begin() as conn:
                    # Add missing required columns
                    for col_name in missing_required:
                        col_spec = required_columns[col_name]
                        print(f"   Adding missing column: {col_name}...")
                        
                        if col_name == 'id':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN id UUID PRIMARY KEY DEFAULT gen_random_uuid()
                            """))
                        elif col_name == 'role':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN role VARCHAR(20) NOT NULL DEFAULT 'sales_rep'
                            """))
                        elif col_name == 'is_active':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN is_active BOOLEAN NOT NULL DEFAULT true
                            """))
                        elif col_name == 'created_at':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN created_at TIMESTAMP NOT NULL DEFAULT NOW()
                            """))
                        elif col_name == 'updated_at':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN updated_at TIMESTAMP NOT NULL DEFAULT NOW()
                            """))
                        elif col_name == 'email':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN email VARCHAR(255) NOT NULL UNIQUE
                            """))
                        elif col_name == 'username':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN username VARCHAR(100) NOT NULL UNIQUE
                            """))
                        elif col_name == 'hashed_password':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN hashed_password VARCHAR(255) NOT NULL
                            """))
                        elif col_name == 'full_name':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN full_name VARCHAR(255) NOT NULL
                            """))
                        
                        print(f"   ✅ Added {col_name}")
                    
                    # Add missing optional columns
                    for col_name in missing_optional:
                        col_spec = optional_columns[col_name]
                        print(f"   Adding optional column: {col_name}...")
                        
                        if col_name == 'last_login':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN last_login TIMESTAMP NULL
                            """))
                        elif col_name == 'profile_picture_url':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN profile_picture_url VARCHAR(500) NULL
                            """))
                        elif col_name == 'company_role':
                            conn.execute(text("""
                                ALTER TABLE users 
                                ADD COLUMN company_role VARCHAR(100) NULL
                            """))
                        
                        print(f"   ✅ Added {col_name}")
                    
                    # Set UUID default for id if missing
                    if 'id' in column_names:
                        result = conn.execute(text("""
                            SELECT column_default 
                            FROM information_schema.columns 
                            WHERE table_name = 'users' 
                            AND column_name = 'id'
                        """))
                        default = result.scalar()
                        if not default or 'gen_random_uuid' not in str(default):
                            print("   Setting UUID default for id column...")
                            conn.execute(text("""
                                ALTER TABLE users 
                                ALTER COLUMN id SET DEFAULT gen_random_uuid()
                            """))
                            print("   ✅ UUID default set")
                    
                    # Set timestamp defaults if missing
                    for col_name in ['created_at', 'updated_at']:
                        if col_name in column_names:
                            result = conn.execute(text(f"""
                                SELECT column_default 
                                FROM information_schema.columns 
                                WHERE table_name = 'users' 
                                AND column_name = '{col_name}'
                            """))
                            default = result.scalar()
                            if not default or 'NOW()' not in str(default):
                                print(f"   Setting NOW() default for {col_name}...")
                                conn.execute(text(f"""
                                    ALTER TABLE users 
                                    ALTER COLUMN {col_name} SET DEFAULT NOW()
                                """))
                                print(f"   ✅ {col_name} default set")
                    
                    # Create indexes if missing
                    print("   Creating indexes...")
                    try:
                        conn.execute(text("""
                            CREATE INDEX IF NOT EXISTS ix_users_email ON users(email)
                        """))
                        print("   ✅ Index on email created")
                    except:
                        pass
                    
                    try:
                        conn.execute(text("""
                            CREATE INDEX IF NOT EXISTS ix_users_username ON users(username)
                        """))
                        print("   ✅ Index on username created")
                    except:
                        pass
                
                print("\n✅ All fixes applied!")
            else:
                print("\n✅ All required columns present - no fixes needed")
            
            # Final verification
            print("\n🔍 Final verification...")
            inspector = inspect(engine)
            columns = inspector.get_columns("users")
            column_names = [col["name"] for col in columns]
            
            all_required = all(col in column_names for col in required_columns.keys())
            
            if all_required:
                print("✅ Users table is ready for sign in/sign up!")
                print(f"\n📊 Table Summary:")
                print(f"   Total columns: {len(column_names)}")
                print(f"   Required columns: ✅ All present")
                print(f"   Optional columns: {len([c for c in optional_columns.keys() if c in column_names])}/{len(optional_columns)}")
                
                # Test query
                print("\n🧪 Testing table access...")
                result = conn.execute(text("SELECT COUNT(*) FROM users"))
                user_count = result.scalar()
                print(f"   Current users: {user_count}")
                print("   ✅ Table is accessible")
                
                return True
            else:
                missing = [c for c in required_columns.keys() if c not in column_names]
                print(f"❌ Missing required columns: {', '.join(missing)}")
                return False
                
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = verify_and_fix_users_table()
    sys.exit(0 if success else 1)

