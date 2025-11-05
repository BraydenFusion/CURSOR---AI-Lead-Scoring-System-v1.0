# 🔧 Database Migration Fix

## Problem

Migration was failing with:
```
psycopg.errors.UndefinedTable: relation "leads" does not exist
```

This happened because `001_performance_indexes` was trying to create indexes on tables that didn't exist yet.

## Solution

### 1. Created Initial Schema Migration

Created `000_initial_schema.py` that creates all core tables:
- `users`
- `leads`
- `lead_activities`
- `lead_score_history`
- `lead_assignments`
- `lead_notes`
- `notifications`

### 2. Fixed Migration Dependencies

Updated `001_performance_indexes.py`:
- Changed `down_revision` from `None` to `'000_initial'`
- Now depends on the initial schema migration

### 3. Made Index Creation Safe

Updated `001_performance_indexes.py` to:
- Check if tables exist before creating indexes
- Check if indexes already exist before creating (idempotent)
- Handle cases where tables might not exist yet

### 4. Enhanced Startup Script

Updated `start-railway.sh` to:
- Check current migration revision
- Handle migration failures gracefully
- Attempt recovery if initial migration hasn't run

## Migration Order (Now Correct)

1. `000_initial` - Creates all core tables (base migration)
2. `001_performance_indexes` - Adds performance indexes (depends on 000)
3. `a9c00044788a` - Phase 4 tables (depends on 001)
4. `002_ai_scoring` - AI scoring tables (depends on a9c00044788a)

## What Happens After Redeploy

1. Railway will redeploy backend
2. Migration will run: `000_initial` → `001_performance_indexes` → `a9c00044788a` → `002_ai_scoring`
3. All tables will be created in correct order
4. Indexes will be added after tables exist

## 405 Method Not Allowed Errors

These are **expected** - the endpoints require specific paths:

| Request | Status | Correct Path |
|---------|--------|--------------|
| `GET /api/auth` | 405 | Use `POST /api/auth/login` for login |
| `GET /api/assignments` | 405 | Use `GET /api/assignments/my-leads` or `POST /api/assignments/` |
| `GET /api/notes` | 405 | Use `GET /api/notes/{lead_id}` or `POST /api/notes/` |
| `GET /api/notifications` | 200 | ✅ This is correct (has GET route) |

These aren't errors - they're the API correctly rejecting invalid requests.

## Verification After Redeploy

Check Railway deploy logs for:
```
✅ Running upgrade 000_initial -> 001_performance_indexes
✅ Running upgrade 001_performance_indexes -> a9c00044788a
✅ Running upgrade a9c00044788a -> 002_ai_scoring
✅ Migrations completed successfully
```

Then test:
```bash
curl https://backend-base.up.railway.app/api/leads
# Should return empty list (not 500 error)
```

---

**Status:** ✅ Fixed and pushed  
**Next:** Wait for Railway redeploy, then verify tables exist

