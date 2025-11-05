# Create Users Table on Railway

## Quick Command

If you want to create the users table on Railway right now, you have two options:

### Option 1: Automatic (Recommended)
The table will be created automatically when Railway redeploys the backend. The `ensure_users_table.py` script runs on every startup and creates the table if it doesn't exist.

**Just wait for Railway to redeploy** - the table will be created automatically.

### Option 2: Manual via Railway CLI

If you have Railway CLI installed:

```bash
# Connect to your Railway project
railway link

# Run the ensure script
railway run python3 ensure_users_table.py
```

### Option 3: Manual via Railway Shell

1. Go to Railway Dashboard → Backend Service
2. Click on "Shell" tab
3. Run:
   ```bash
   python3 ensure_users_table.py
   ```

### Option 4: Direct SQL (if above don't work)

1. Go to Railway Dashboard → PostgreSQL Service
2. Click on "Data" tab (or use Railway CLI: `railway connect postgresql`)
3. Run this SQL:

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
```

## Verify Table Exists

After creating, verify with:

```bash
railway run python3 verify_users_table.py
```

Or check Railway deploy logs for:
- `✅ Users table verified/created successfully`

## Current Status

The `ensure_users_table.py` script runs automatically on every Railway deployment. If the table doesn't exist, it will be created automatically.

**No manual action needed** - just wait for the next Railway deployment or trigger a redeploy.

