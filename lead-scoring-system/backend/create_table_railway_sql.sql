-- ============================================
-- Create Users Table on Railway - Run this SQL
-- ============================================
-- Copy and paste this entire script into Railway's Database SQL editor
-- Railway Dashboard → PostgreSQL → Database tab → Data sub-tab → SQL Editor
-- ============================================

-- Step 1: Create user_role enum type
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'sales_rep');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Step 2: Create users table
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

-- Step 3: Create indexes for performance
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);

-- Step 4: Verify table was created
SELECT 
    'users table created successfully' AS status,
    COUNT(*) AS current_user_count
FROM users;

-- ============================================
-- Expected Result:
-- status: users table created successfully
-- current_user_count: 0
-- ============================================

