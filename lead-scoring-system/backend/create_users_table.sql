-- ============================================
-- Users Table Creation Script
-- ============================================
-- This script creates the complete users table with all fields
-- Note: On Railway, this is handled automatically by Alembic migrations
-- Use this as a reference or for manual database setup
-- ============================================

-- Create user_role enum type (if not exists)
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('admin', 'manager', 'sales_rep');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create users table (drop if exists for fresh start - use with caution!)
-- DROP TABLE IF EXISTS users CASCADE;

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
    company_role VARCHAR(100) NULL,
    
    -- Constraints
    CONSTRAINT chk_email_format CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$')
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_username ON users(username);
CREATE INDEX IF NOT EXISTS ix_users_role ON users(role);
CREATE INDEX IF NOT EXISTS ix_users_is_active ON users(is_active);

-- Create function to automatically update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create trigger to auto-update updated_at
DROP TRIGGER IF EXISTS update_users_updated_at ON users;
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Table Structure Summary:
-- ============================================
-- id: UUID (Primary Key)
-- email: VARCHAR(255) - Unique, indexed
-- username: VARCHAR(100) - Unique, indexed
-- hashed_password: VARCHAR(255) - bcrypt hashed password
-- full_name: VARCHAR(255)
-- role: ENUM ('admin', 'manager', 'sales_rep') - Default: 'sales_rep'
-- is_active: BOOLEAN - Default: true
-- created_at: TIMESTAMP - Auto-set on creation
-- updated_at: TIMESTAMP - Auto-updated on modification
-- last_login: TIMESTAMP - Tracks last login time
-- profile_picture_url: VARCHAR(500) - URL to profile picture
-- company_role: VARCHAR(100) - User's company role (e.g., "Sales Manager")
-- ============================================

-- Verify table creation
SELECT 
    'users table created successfully' AS status,
    COUNT(*) AS current_user_count
FROM users;

