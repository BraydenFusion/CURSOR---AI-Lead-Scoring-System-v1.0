# Creating the Leads Table on Railway

Since Railway doesn't have a SQL editor, you'll need to use Railway Shell or CLI to create the leads table.

## Option 1: Using Railway Shell (Recommended)

1. **Go to Railway Dashboard**
   - Navigate to your **Backend Service**
   - Click on the **Shell** tab

2. **Run the script**
   ```bash
   python3 create_leads_table_railway.py
   ```

3. **If it asks about dropping existing table**
   - Type `N` (or just press Enter) to keep existing table
   - Type `y` if you want to recreate it

## Option 2: Using Railway CLI

1. **Install Railway CLI** (if not already installed)
   ```bash
   npm i -g @railway/cli
   ```

2. **Link to your project**
   ```bash
   railway link
   ```

3. **Connect to PostgreSQL**
   ```bash
   railway connect postgresql
   ```

4. **Run the script**
   ```bash
   python3 create_leads_table_railway.py
   ```

## What the Script Does

The script will:
1. ✅ Create `lead_classification` enum (hot, warm, cold)
2. ✅ Create `lead_status` enum (new, contacted, qualified, proposal, negotiation, won, lost)
3. ✅ Create `leads` table with all required columns:
   - `id` (UUID, primary key)
   - `name` (VARCHAR 255)
   - `email` (VARCHAR 255, unique)
   - `phone` (VARCHAR 50, nullable)
   - `source` (VARCHAR 100)
   - `location` (VARCHAR 255, nullable)
   - `current_score` (INTEGER, 0-100)
   - `classification` (enum, nullable)
   - `status` (enum, default: 'new')
   - `contacted_at` (TIMESTAMP, nullable)
   - `qualified_at` (TIMESTAMP, nullable)
   - `closed_at` (TIMESTAMP, nullable)
   - `created_at` (TIMESTAMP, auto)
   - `updated_at` (TIMESTAMP, auto)
   - `metadata` (JSONB, default: {})
   - `created_by` (UUID, foreign key to users.id, nullable)
4. ✅ Create indexes on:
   - `email`
   - `status`
   - `classification`
   - `current_score`
   - `created_at`
   - `created_by`

## Verification

After running the script, you should see:
```
✅ leads table created successfully!
   Total columns: 16
   Column names: id, name, email, phone, source, location, current_score, classification, status, contacted_at, qualified_at, closed_at, created_at, updated_at, metadata, created_by
   ✅ All required columns present
```

## Troubleshooting

If you get an error:
- **"DATABASE_URL not set"**: Make sure PostgreSQL service is connected to Backend service in Railway
- **"relation 'users' does not exist"**: Create the users table first using `create_users_table_railway.py`
- **"permission denied"**: Make sure you're running the script from the backend service Shell

## Next Steps

After creating the leads table:
1. The backend migrations will automatically detect it exists
2. You can now create leads via the API
3. The AI scoring system will be able to score leads
4. All lead-related features will be functional

