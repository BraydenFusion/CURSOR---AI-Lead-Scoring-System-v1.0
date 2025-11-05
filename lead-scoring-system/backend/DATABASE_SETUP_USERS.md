# Database Setup: Users Table

## Overview

The `users` table stores all user account information including authentication credentials, profile data, and role assignments.

## Table Structure

The users table includes the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key, auto-generated |
| `email` | VARCHAR(255) | Unique email address (indexed) |
| `username` | VARCHAR(100) | Unique username (indexed) |
| `hashed_password` | VARCHAR(255) | bcrypt hashed password |
| `full_name` | VARCHAR(255) | User's full name |
| `role` | ENUM | User role: 'admin', 'manager', 'sales_rep' |
| `is_active` | BOOLEAN | Account active status (default: true) |
| `created_at` | TIMESTAMP | Account creation time |
| `updated_at` | TIMESTAMP | Last update time (auto-updated) |
| `last_login` | TIMESTAMP | Last login timestamp (nullable) |
| `profile_picture_url` | VARCHAR(500) | Profile picture URL (nullable) |
| `company_role` | VARCHAR(100) | Company role (e.g., "Sales Manager") (nullable) |

## Automatic Creation (Railway)

On Railway, the users table is **automatically created** when the backend service starts via:

1. **Alembic Migrations** - Run automatically in `start-railway.sh`
2. Migration sequence:
   - `000_initial_schema.py` - Creates base users table
   - `004_add_profile_picture.py` - Adds profile_picture_url
   - `005_add_company_role.py` - Adds company_role

## Manual Setup (If Needed)

### Option 1: Run Migrations (Recommended)

```bash
cd backend
alembic upgrade head
```

This will run all migrations in order and create the complete table.

### Option 2: Use SQL Script

For reference or manual setup:

```bash
# Connect to your PostgreSQL database
psql $DATABASE_URL -f create_users_table.sql
```

### Option 3: Verify Table Exists

Check if the table is properly set up:

```bash
cd backend
python verify_users_table.py
```

This will:
- ✅ Check if table exists
- ✅ Verify all columns are present
- ✅ Check indexes
- ✅ Show current user count
- ✅ Display table structure

## Verification

### Check Table Exists (via SQL)

```sql
SELECT table_name 
FROM information_schema.tables 
WHERE table_schema = 'public' 
AND table_name = 'users';
```

### Check Table Structure

```sql
\d users
-- or
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'users'
ORDER BY ordinal_position;
```

### Check Current Users

```sql
SELECT id, username, email, role, is_active, created_at
FROM users
ORDER BY created_at DESC;
```

## Railway Deployment

On Railway, the table is created automatically:

1. **Backend Service Starts**
2. **`start-railway.sh` runs** → Executes `alembic upgrade head`
3. **Migrations run in order:**
   - Creates `users` table (base structure)
   - Adds `profile_picture_url` column
   - Adds `company_role` column
4. **Table is ready** for user registration/login

## Troubleshooting

### Table doesn't exist

**Symptoms:** `relation "users" does not exist`

**Solution:**
```bash
# Check migration status
cd backend
alembic current

# Run migrations
alembic upgrade head

# Verify
python verify_users_table.py
```

### Missing columns

**Symptoms:** `column "profile_picture_url" does not exist`

**Solution:**
```bash
# Check which migrations have run
alembic current

# Run all migrations
alembic upgrade head

# Or run specific migration
alembic upgrade 004_profile_picture
alembic upgrade 005_company_role
```

### Check Migration Status on Railway

1. Go to Railway Dashboard → Backend Service
2. View Deploy Logs
3. Look for: `🔄 Running database migrations...`
4. Should see: `✅ Migrations completed successfully`

## Example: Create User via SQL

```sql
-- Insert a test user (password will be hashed in application)
INSERT INTO users (
    email, 
    username, 
    full_name, 
    hashed_password, 
    role, 
    is_active,
    company_role
) VALUES (
    'test@example.com',
    'testuser',
    'Test User',
    '$2b$12$...', -- bcrypt hash (use application to generate)
    'sales_rep',
    true,
    'Sales Representative'
);
```

**Note:** Always use the application's password hashing function. Don't insert plain text passwords!

## Related Files

- **Model Definition:** `backend/app/models/user.py`
- **Migration 000:** `backend/alembic/versions/000_initial_schema.py`
- **Migration 004:** `backend/alembic/versions/004_add_profile_picture.py`
- **Migration 005:** `backend/alembic/versions/005_add_company_role.py`
- **SQL Reference:** `backend/create_users_table.sql`
- **Verification Script:** `backend/verify_users_table.py`

