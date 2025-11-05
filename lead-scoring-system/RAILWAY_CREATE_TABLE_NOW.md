# 🚨 Create Users Table on Railway RIGHT NOW

## The Problem
Only `alembic_version` table exists - migrations didn't create the `users` table.

## Quick Fix: Run SQL Directly

### Step 1: Open Railway Database SQL Editor
1. Go to **Railway Dashboard**
2. Click on **DATABASE** service (the one at the top)
3. Click **Database** tab
4. Click **Data** sub-tab
5. Look for **SQL Editor** or **Query** button (usually at the top right)

### Step 2: Copy and Paste This SQL

```sql
-- Create user_role enum type
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'sales_rep');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create users table
CREATE TABLE IF NOT EXISTS users (
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
);

-- Create indexes
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

-- Verify
SELECT 'users table created' AS status, COUNT(*) AS user_count FROM users;
```

### Step 3: Run the SQL
Click **Run** or **Execute** button

### Step 4: Verify
You should see:
- `status: users table created`
- `user_count: 0`

Refresh the **Tables** list - you should now see `users` table!

---

## Alternative: Use Railway CLI

If you have Railway CLI installed:

```bash
# 1. Connect to your project
railway link

# 2. Connect to PostgreSQL
railway connect postgresql

# 3. Run the SQL script
psql < create_table_railway_sql.sql
```

Or use the Python script:

```bash
railway run python3 ensure_users_table.py
```

---

## Why This Happened

The migrations ran but didn't actually execute the CREATE TABLE statements. This could be because:
- Migration chain is broken
- Migration files have errors
- Database connection issues during migration

The SQL above will create the table directly, bypassing migrations.

---

## After Creating the Table

1. **Test login** - Should work now!
2. **Test registration** - Should work now!
3. **Check Railway logs** - Look for `✅ Users table verified/created successfully`

---

## Need Help?

If the SQL doesn't work, check:
1. Are you connected to the correct database?
2. Do you have CREATE TABLE permissions?
3. Check Railway logs for any errors

