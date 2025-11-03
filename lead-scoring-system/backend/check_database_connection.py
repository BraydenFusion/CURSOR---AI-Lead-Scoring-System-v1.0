#!/usr/bin/env python3
"""Quick script to check if DATABASE_URL is configured and test connection."""

import os
import sys

print("🔍 Checking Database Configuration...")
print("=" * 60)

# Check if DATABASE_URL is set
database_url = os.getenv("DATABASE_URL", "")

if not database_url:
    print("❌ DATABASE_URL environment variable is NOT set!")
    print("")
    print("SOLUTION:")
    print("1. Railway Dashboard → PostgreSQL Service")
    print("2. Click 'Connect Service' → Select Backend service")
    print("3. Railway will automatically set DATABASE_URL")
    print("")
    sys.exit(1)

print(f"✅ DATABASE_URL is set (length: {len(database_url)})")

# Check if it's using localhost (wrong)
if "localhost:5433" in database_url or "127.0.0.1:5433" in database_url:
    print("❌ DATABASE_URL is set to localhost (127.0.0.1:5433)")
    print("   This means Railway PostgreSQL is not connected!")
    print("")
    print("SOLUTION:")
    print("   Connect PostgreSQL service to Backend service in Railway")
    print("")
    sys.exit(1)

# Check if it's a Railway URL (correct)
if ".railway.app" in database_url or "railway" in database_url.lower():
    print("✅ DATABASE_URL appears to be a Railway URL")
else:
    print("⚠️  DATABASE_URL doesn't look like a Railway URL")

# Test connection
print("")
print("Testing database connection...")

try:
    from app.database import engine
    from sqlalchemy import text
    
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        result.fetchone()
    
    print("✅ Database connection successful!")
    print("")
    print("You can now create users and test the login.")
    sys.exit(0)
except Exception as e:
    print(f"❌ Database connection failed: {e}")
    print("")
    print("Please check:")
    print("  1. PostgreSQL service is running in Railway")
    print("  2. DATABASE_URL is correct")
    print("  3. Network connectivity")
    sys.exit(1)

