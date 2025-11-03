# 🧪 Quick Test Guide - After Migrations Complete

Use this guide to quickly verify everything is working after Railway redeploys.

---

## ✅ Step 1: Verify Database Connection (30 seconds)

```bash
curl https://your-backend.railway.app/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "timestamp": "2025-11-03T18:00:00",
  "environment": "production"
}
```

**✅ Pass:** Database shows "connected"  
**❌ Fail:** If still shows "disconnected", check Railway deploy logs

---

## ✅ Step 2: Verify Migrations Ran (1 minute)

**Check Deploy Logs:**
1. Railway Dashboard → Backend Service → Deployments → Latest
2. Look for:
   ```
   🔄 Running database migrations from /app...
   📄 Found alembic.ini at /app/alembic.ini
   INFO [alembic.runtime.migration] Running upgrade ...
   ```

**✅ Pass:** See "Running upgrade" message  
**❌ Fail:** See "alembic.ini not found" → Check Dockerfile or use Railway CLI

---

## ✅ Step 3: Register a Test User (1 minute)

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
  "id": "uuid-here",
  "email": "test@example.com",
  "username": "testuser",
  "full_name": "Test User",
  "role": "sales_rep",
  "is_active": true
}
```

**✅ Pass:** User created with 201 status  
**❌ Fail:** Check error message (likely database issue)

---

## ✅ Step 4: Login and Get Token (30 seconds)

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

**Save Token:**
```bash
export TOKEN="paste-your-token-here"
```

**✅ Pass:** Receive access_token  
**❌ Fail:** Invalid credentials or database error

---

## ✅ Step 5: Create Lead (Auto-Scoring Test) (1 minute)

```bash
curl -X POST https://your-backend.railway.app/api/leads \
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
  }'
```

**Expected Response:**
```json
{
  "id": "uuid-here",
  "name": "Sarah Johnson",
  "email": "sarah.j@example.com",
  "current_score": 85,
  "classification": "hot",
  ...
}
```

**Key Checks:**
- ✅ `current_score` is > 0 (auto-scored)
- ✅ `classification` is "hot", "warm", or "cold"
- ✅ Status 201 Created

**✅ Pass:** Lead created with score  
**❌ Fail:** Check error - might be missing AI scoring tables

---

## ✅ Step 6: Get AI Score Breakdown (30 seconds)

```bash
# Replace {lead_id} with actual ID from Step 5
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
  "scored_at": "2025-11-03T18:00:00",
  "insights": [
    {
      "type": "talking_point",
      "content": "Time-sensitive request detected...",
      "confidence": 0.88
    }
  ]
}
```

**Key Checks:**
- ✅ All component scores present (engagement, buying, demographic)
- ✅ `priority_tier` matches score (HOT ≥80, WARM ≥50, COLD <50)
- ✅ `insights` array has at least one item
- ✅ `confidence_level` between 0.0-1.0

**✅ Pass:** Detailed score with insights  
**❌ Fail:** May indicate AI scoring service issue

---

## ✅ Step 7: Get Prioritized Leads (30 seconds)

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
      "score": 85,
      "priority_tier": "HOT",
      "insights": [...],
      "suggested_actions": [...]
    }
  ],
  "total_hot": 1,
  "total_warm": 0,
  "total_cold": 0
}
```

**Key Checks:**
- ✅ Leads sorted by score (highest first)
- ✅ Each lead has `insights` and `suggested_actions`
- ✅ `total_hot/warm/cold` counts accurate

**✅ Pass:** Prioritized list with insights  
**❌ Fail:** May indicate query or scoring issue

---

## 🎯 Success Criteria

**All Systems Operational If:**
- ✅ Health check shows database connected
- ✅ Migrations ran without errors
- ✅ User registration works
- ✅ Login returns token
- ✅ Lead creation auto-scores
- ✅ AI scoring endpoint returns detailed breakdown
- ✅ Prioritized endpoint returns sorted leads with insights

---

## 🚨 If Tests Fail

### Database Connection Fails
- Check Railway: Backend → Variables → DATABASE_URL
- Verify it's a Reference Variable linked to DATABASE service
- Check deploy logs for connection errors

### Migrations Don't Run
- Check deploy logs for "alembic.ini not found"
- Verify Dockerfile copied files correctly
- Use Railway CLI: `railway run alembic upgrade head`

### Scoring Returns 0 or Errors
- Verify tables exist: `lead_scores`, `lead_engagement_events`, `lead_insights`
- Check deploy logs for table creation errors
- Verify migration ran successfully

### API Endpoints Return 404
- Check that routes are registered: `/debug/routes`
- Verify backend is running: `/health`
- Check Railway deploy logs for startup errors

---

## 📊 Expected Results Summary

| Test | Expected Status | Key Indicator |
|------|----------------|---------------|
| Health Check | 200 OK | `"database": "connected"` |
| Migration | Success | "Running upgrade" in logs |
| User Registration | 201 Created | User object returned |
| Login | 200 OK | `access_token` present |
| Create Lead | 201 Created | `current_score` > 0 |
| AI Score | 200 OK | All scores + insights |
| Prioritized | 200 OK | Sorted leads + counts |

---

**Total Testing Time:** ~5 minutes  
**All Tests Pass?** ✅ System is ready for production use!

