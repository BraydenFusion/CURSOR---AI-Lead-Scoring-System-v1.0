# Create Users Table on Railway (No SQL Editor Available)

Railway's database interface doesn't have an SQL editor, but you can create the table using Railway Shell or CLI.

## Option 1: Railway Shell (Easiest)

### Step 1: Open Railway Shell
1. Go to **Railway Dashboard**
2. Click on **BACKEND** service (not DATABASE)
3. Click **Shell** tab
4. You'll see a terminal prompt

### Step 2: Run the Script
```bash
cd /app
python3 create_users_table_railway.py
```

### Step 3: Verify
The script will:
- ✅ Check if table exists
- ✅ Create the table if it doesn't exist
- ✅ Show table structure
- ✅ Confirm success

---

## Option 2: Railway CLI

If you have Railway CLI installed:

```bash
# 1. Connect to your project
railway link

# 2. Run the script in backend service
railway run --service backend python3 create_users_table_railway.py
```

---

## Option 3: Use Backend Service → Shell → Direct SQL

If Railway Shell doesn't work, you can also connect to PostgreSQL directly:

```bash
# In Railway Shell (BACKEND service)
railway connect postgresql

# Then run SQL commands
psql
```

Then paste this SQL:
```sql
-- Create enum type
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

---

## Recommended: Use Option 1 (Railway Shell)

The easiest way is to use Railway Shell on the **BACKEND** service and run:
```bash
python3 create_users_table_railway.py
```

This script:
- ✅ Uses the correct database connection (from app.config)
- ✅ Handles all the SQL for you
- ✅ Verifies the table was created
- ✅ Shows you the table structure

---

## After Creating the Table

1. **Refresh Railway Dashboard** → DATABASE → Database → Data
2. You should now see the `users` table in the list
3. **Test login/registration** - should work now!

