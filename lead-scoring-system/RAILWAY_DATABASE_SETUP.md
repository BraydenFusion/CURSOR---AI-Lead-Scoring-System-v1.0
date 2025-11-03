# 🔧 Railway Database Setup & Testing Guide

## Step 1: Fix DATABASE_URL Connection

### Option A: Using "Connect Service" (Recommended)

1. **Go to Railway Dashboard**
   - Navigate to: https://railway.app/dashboard
   - Open your project

2. **Find PostgreSQL Service**
   - In your project, you should see a PostgreSQL service
   - Click on the PostgreSQL service card

3. **Connect to Backend Service**
   - In the PostgreSQL service page, look for a button/section that says:
     - "Connect Service" OR
     - "Share Variables" OR
     - "Generate Connection String"
   - Click on it
   - A modal/popup should appear

4. **Select Backend Service**
   - From the dropdown, select your **Backend** service
   - Click "Connect" or "Generate"

5. **Verify Connection**
   - Go to your **Backend** service in Railway
   - Click on the "Variables" tab
   - Look for `DATABASE_URL` in the list
   - It should show a green checkmark or "Connected" status
   - The value should start with `postgresql://` or `postgres://`

### Option B: Manual Copy-Paste (If Option A doesn't work)

1. **Get DATABASE_URL from PostgreSQL**
   - Go to Railway Dashboard → Your Project
   - Click on **PostgreSQL Service**
   - Click on the **Variables** tab
   - Find the `DATABASE_URL` variable
   - Click on it to reveal the full value
   - **Copy the ENTIRE URL** (it's long, looks like: `postgresql://user:password@hostname:port/database`)

2. **Set DATABASE_URL in Backend**
   - Go to Railway Dashboard → Your Project
   - Click on **Backend Service**
   - Click on the **Variables** tab
   - Click **"New Variable"** or **"Add Variable"**
   - Name: `DATABASE_URL`
   - Value: [Paste the FULL URL you copied]
   - **IMPORTANT:** 
     - ✅ Use the ACTUAL URL (not `${{ Postgres.DATABASE_URL }}`)
     - ✅ Include the entire string from `postgresql://` to the end
     - ✅ No quotes needed
   - Click **"Add"** or **"Save"**

3. **Verify**
   - The variable should appear in your Backend Variables list
   - Railway will automatically redeploy your backend service
   - Wait 2-3 minutes for deployment to complete

### Verify Database Connection

1. **Check Backend Deploy Logs**
   - Go to Backend Service → Deployments → Latest deployment
   - Look for logs that show:
     - `✅ Database connection successful` OR
     - Database URL starting with your PostgreSQL hostname (not `localhost`)

2. **Check Health Dashboard**
   - Visit: `https://your-backend.railway.app/health`
   - Should show:
     - `"database": "connected"` (NOT "disconnected")
     - `"status": "healthy"` (NOT "degraded")
     - Connection pool metrics visible

3. **If Still Not Working**
   - Visit: `https://your-backend.railway.app/debug/database-url`
   - Check what URL is actually being used
   - Verify it's not `localhost:5433`

---

## Step 2: Run Database Migration

### Automatic (Recommended - Runs on Startup)

The migration will run automatically when the backend starts because `start-railway.sh` includes:

```bash
cd /app && alembic upgrade head
```

**To verify it ran:**
1. Check backend deploy logs
2. Look for: `🔄 Running database migrations...`
3. Should see: `INFO [alembic.runtime.migration] Running upgrade ...`

### Manual (If Needed)

If you need to run it manually:

1. **Open Railway Shell**
   - Go to Backend Service in Railway
   - Click on "Deployments" tab
   - Click on the latest deployment
   - Look for "Shell" or "Terminal" button (if available)
   - OR use Railway CLI:

2. **Using Railway CLI** (if installed):
   ```bash
   # Install Railway CLI (if not installed)
   npm i -g @railway/cli
   
   # Login
   railway login
   
   # Link to your project
   railway link
   
   # Run migration
   railway run alembic upgrade head
   ```

3. **Verify Migration Success**
   - Check logs for: `Running upgrade a9c00044788a -> 002_ai_scoring`
   - Should see: `INFO [alembic.runtime.migration] Running upgrade 002_ai_scoring`
   - No errors should appear

### Verify Tables Created

You can verify the tables exist by:

1. **Using PostgreSQL Service in Railway**
   - Go to PostgreSQL Service → Data tab
   - Look for tables: `lead_scores`, `lead_engagement_events`, `lead_insights`

2. **Using API Endpoint** (after backend is running):
   - Visit: `https://your-backend.railway.app/debug/routes`
   - Should show all routes including new scoring endpoints

---

## Step 3: Test Scoring System End-to-End

### Test 1: Create a User (If Not Already Done)

**Using API:**
```bash
curl -X POST https://your-backend.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "testpass123"
  }'
```

**Expected Response:**
```json
{
  "id": "uuid",
  "email": "test@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "role": "sales_rep",
  "is_active": true
}
```

---

### Test 2: Login and Get Token

```bash
curl -X POST https://your-backend.railway.app/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123"
```

**Expected Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "user": {...}
}
```

**Save the token:**
```bash
export TOKEN="your_access_token_here"
```

---

### Test 3: Create a Lead (Auto-Scoring Test)

```bash
curl -X POST https://your-backend.railway.app/api/leads \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Sarah Johnson",
    "email": "sarah.j@example.com",
    "phone": "555-123-4567",
    "source": "website",
    "location": "New York, NY",
    "metadata": {
      "vehicle_interest": "2024 Honda Accord",
      "budget_min": 28000,
      "budget_max": 32000,
      "initial_message": "I need a car by Friday ASAP"
    }
  }'
```

**Expected Response:**
```json
{
  "id": "uuid",
  "name": "Sarah Johnson",
  "email": "sarah.j@example.com",
  "current_score": 85,
  "classification": "hot",
  ...
}
```

**What Happened:**
- Lead was created
- AI scoring automatically ran
- Score was calculated based on:
  - Engagement (35 pts max)
  - Buying signals (40 pts max) - urgency keywords detected!
  - Demographic fit (25 pts max) - budget and vehicle interest provided
- Priority tier assigned (HOT/WARM/COLD)

---

### Test 4: Manually Score a Lead (AI Scoring Endpoint)

```bash
curl -X POST https://your-backend.railway.app/api/leads/{lead_id}/score \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "lead_id": "uuid",
  "overall_score": 85,
  "engagement_score": 32,
  "buying_signal_score": 38,
  "demographic_score": 24,
  "priority_tier": "HOT",
  "confidence_level": 0.87,
  "scored_at": "2025-11-03T16:00:00",
  "insights": [
    {
      "type": "talking_point",
      "content": "Time-sensitive request detected - emphasize quick delivery",
      "confidence": 0.88
    },
    {
      "type": "talking_point",
      "content": "Interested in 2024 Honda Accord with budget up to $32,000",
      "confidence": 0.75
    }
  ],
  "scoring_metadata": {
    "algorithm_version": "1.0",
    "calculated_at": "2025-11-03T16:00:00Z"
  }
}
```

**Verify:**
- ✅ `overall_score` is between 0-100
- ✅ Component scores add up correctly
- ✅ `priority_tier` matches score (HOT ≥80, WARM ≥50, COLD <50)
- ✅ `confidence_level` is between 0.0-1.0
- ✅ `insights` array has talking points

---

### Test 5: Get Prioritized Leads (Top 5)

```bash
curl -X GET "https://your-backend.railway.app/api/leads/prioritized?limit=5" \
  -H "Authorization: Bearer $TOKEN"
```

**Expected Response:**
```json
{
  "leads": [
    {
      "id": "uuid",
      "name": "Sarah Johnson",
      "email": "sarah.j@example.com",
      "phone": "555-123-4567",
      "score": 85,
      "priority_tier": "HOT",
      "vehicle_interest": "2024 Honda Accord",
      "budget_range": "$28,000-$32,000",
      "time_since_inquiry": "2 minutes",
      "insights": [
        {
          "type": "talking_point",
          "content": "Time-sensitive request...",
          "confidence": 0.88
        }
      ],
      "suggested_actions": [
        "💡 Time-sensitive request detected...",
        "💡 Interested in 2024 Honda Accord..."
      ]
    }
  ],
  "total_hot": 1,
  "total_warm": 0,
  "total_cold": 0
}
```

**Verify:**
- ✅ Leads sorted by score (highest first)
- ✅ Each lead has `insights` array
- ✅ `suggested_actions` populated from insights
- ✅ `time_since_inquiry` is human-readable
- ✅ `total_hot`, `total_warm`, `total_cold` counts accurate

---

### Test 6: Add Engagement Events (Test Real-Time Scoring)

To test engagement scoring, you need to create engagement events. For now, these would be created by external systems (website tracking, email service), but you can test manually:

**Note:** The engagement events system needs to be integrated with your website/email system. For now, you can verify the scoring works with existing activities.

**Check if score updates:**
1. Create a lead with initial score
2. Add activities/notes to the lead
3. Call `POST /api/leads/{id}/score` again
4. Verify score has changed based on new activities

---

## Step 4: Verify Database Tables

### Check Tables Exist

1. **Via PostgreSQL Service in Railway**
   - Go to PostgreSQL → Data tab
   - Should see: `lead_scores`, `lead_engagement_events`, `lead_insights`

2. **Via API (if you add a debug endpoint)**
   - Can check `/debug/database-url` for connection status

### Verify Data Stored

After running tests above, verify data was stored:

1. **Check lead_scores table**
   - Should have rows with scores, priority_tiers, confidence_levels

2. **Check lead_insights table**
   - Should have rows with talking points generated for scored leads

---

## Troubleshooting

### Issue: DATABASE_URL Still Shows localhost

**Solution:**
1. Double-check you copied the FULL URL from PostgreSQL
2. Verify there are no `${{ }}` variable references
3. Check Backend Variables tab - DATABASE_URL should show the actual URL
4. Redeploy backend service manually if needed

### Issue: Migration Fails

**Error:** `Table 'lead_scores' already exists`

**Solution:**
- Table might already exist from previous migration
- Check if migration already ran
- Run: `alembic current` to see current revision
- If already at `002_ai_scoring`, migration is complete

**Error:** `Could not resolve revision`

**Solution:**
- Make sure migration file exists: `backend/alembic/versions/002_add_ai_scoring_tables.py`
- Check migration history: `alembic history`

### Issue: Scoring Returns 0 or Low Scores

**Possible Causes:**
1. No engagement events yet (normal for new leads)
2. Missing metadata (budget, vehicle_interest)
3. No activities logged for the lead

**Solution:**
- Create leads with complete data (metadata with budget, vehicle_interest)
- Add some activities to test engagement scoring
- Check that metadata is stored in `lead._metadata` field

### Issue: Prioritized Endpoint Returns Empty List

**Possible Causes:**
1. No leads have been scored yet
2. User doesn't have assigned leads (for sales reps)
3. All leads have score = 0

**Solution:**
- Make sure you've created at least one lead
- Make sure that lead has been scored (auto-scored on creation)
- For sales reps: assign a lead first
- For admins/managers: should see all leads

---

## Quick Test Script

Save this as `test_scoring.sh`:

```bash
#!/bin/bash

# Set your backend URL
BACKEND_URL="https://your-backend.railway.app"

# Test 1: Register user
echo "1. Registering user..."
REGISTER_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "full_name": "Test User",
    "password": "testpass123"
  }')

echo "Register response: $REGISTER_RESPONSE"

# Test 2: Login
echo "2. Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=testuser&password=testpass123")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)
echo "Token: ${TOKEN:0:50}..."

# Test 3: Create lead
echo "3. Creating lead..."
LEAD_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/leads" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{
    "name": "Sarah Johnson",
    "email": "sarah.j@example.com",
    "phone": "555-123-4567",
    "source": "website",
    "metadata": {
      "vehicle_interest": "2024 Honda Accord",
      "budget_max": 32000,
      "initial_message": "I need a car by Friday ASAP"
    }
  }')

LEAD_ID=$(echo $LEAD_RESPONSE | grep -o '"id":"[^"]*' | cut -d'"' -f4)
echo "Lead ID: $LEAD_ID"
echo "Lead score: $(echo $LEAD_RESPONSE | grep -o '"current_score":[0-9]*' | cut -d':' -f2)"

# Test 4: Score lead
echo "4. Scoring lead with AI..."
SCORE_RESPONSE=$(curl -s -X POST "$BACKEND_URL/api/leads/$LEAD_ID/score" \
  -H "Authorization: Bearer $TOKEN")

echo "AI Score Response:"
echo $SCORE_RESPONSE | python3 -m json.tool

# Test 5: Get prioritized
echo "5. Getting prioritized leads..."
PRIORITIZED_RESPONSE=$(curl -s -X GET "$BACKEND_URL/api/leads/prioritized?limit=5" \
  -H "Authorization: Bearer $TOKEN")

echo "Prioritized Leads:"
echo $PRIORITIZED_RESPONSE | python3 -m json.tool

echo "✅ All tests complete!"
```

**Usage:**
```bash
chmod +x test_scoring.sh
./test_scoring.sh
```

---

## Success Indicators

✅ **Database Connected:**
- `/health` shows `"database": "connected"`
- No "localhost" or "127.0.0.1" in database URL

✅ **Migration Complete:**
- Backend logs show migration ran successfully
- Tables exist in PostgreSQL

✅ **Scoring Works:**
- Lead creation auto-scores with non-zero values
- `POST /api/leads/{id}/score` returns detailed breakdown
- Insights array is populated
- Priority tier is assigned correctly

✅ **Prioritized Endpoint Works:**
- Returns leads sorted by score
- Shows insights and suggested actions
- Role-based filtering works (sales reps see only assigned)

---

**Need Help?**
- Check `/health` dashboard for system status
- Check `/debug/database-url` for DATABASE_URL verification
- Check backend deploy logs in Railway for errors
- Review SYSTEM_STATUS.md for known issues

