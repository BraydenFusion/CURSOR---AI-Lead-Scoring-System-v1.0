# 🔧 Fix Railway Variable Reference Issue

## Problem
You set `DATABASE_URL = ${{ Postgres.DATABASE_URL }}` but it's not working.

**Why:** Railway variable references `${{ Service.VARIABLE }}` sometimes don't resolve correctly, or the service name doesn't match.

---

## ✅ Solution 1: Use "Connect Service" (Recommended)

Instead of using variable references, use Railway's **"Connect Service"** feature:

### Steps:

1. **Go to PostgreSQL Service** in Railway Dashboard
2. **Click "Variables"** tab (or "Connect" tab)
3. **Find "Connect Service"** button (not "Variables")
4. **Click "Connect Service"**
5. **Select your Backend service** from dropdown
6. Railway automatically sets `DATABASE_URL` in backend (no manual variable needed)

**This is the proper Railway way** - it creates a service connection and auto-injects `DATABASE_URL`.

---

## ✅ Solution 2: Fix Variable Reference (If Connect Doesn't Work)

### Step 1: Find Actual Service Name

1. Go to your **PostgreSQL service**
2. Click on **"Variables"** tab
3. Look at the **service name** in Railway
   - It might be "Postgres", "PostgreSQL", or something else
   - Note the **exact** name (case-sensitive)

### Step 2: Check Available Variables

In PostgreSQL → Variables, you should see:
- `DATABASE_URL`
- `PGDATABASE`
- `PGHOST`
- `PGPORT`
- `PGUSER`
- `PGPASSWORD`

### Step 3: Update Backend Variable

1. Go to **Backend Service** → **Variables**
2. Find your `DATABASE_URL` variable
3. **Click to edit it**

**Try these options (one at a time):**

**Option A - Check service name:**
```
${{ Postgres.DATABASE_URL }}
```
(If your service is named "Postgres")

**Option B - Try PostgreSQL:**
```
${{ PostgreSQL.DATABASE_URL }}
```
(If your service is named "PostgreSQL")

**Option C - Try exact service name:**
Look at your PostgreSQL service card in Railway - use that exact name.

**Option D - Use PGDATABASE instead:**
```
${{ Postgres.PGDATABASE }}
```

### Step 4: Redeploy and Check Logs

After updating, redeploy backend and check logs.

**If it's working, you'll see:**
```
✅ DATABASE_URL found in environment (length: XXX)
Database URL: postgresql+psycopg://***:***@xxxxx.railway.app:5432/railway
```

**If it's NOT working, you'll see:**
```
⚠️  DATABASE_URL appears to be an unresolved Railway reference: ${{ Postgres.DATABASE_URL }}
⚠️  This means the variable reference is not resolving!
```

---

## ✅ Solution 3: Manual Copy (Last Resort)

If variable references don't work:

1. **Go to PostgreSQL Service** → **Variables**
2. **Find `DATABASE_URL`**
3. **Click to reveal the value** (eye icon or click)
4. **Copy the entire URL**
5. **Go to Backend Service** → **Variables**
6. **Edit `DATABASE_URL`**
7. **Paste the actual URL** (not the reference)
8. **Save**

**Example:**
Instead of: `${{ Postgres.DATABASE_URL }}`

Use: `postgres://postgres:actualpassword@containers-us-west-xxx.railway.app:5432/railway`

---

## 🔍 Verify Variable Reference is Working

### Check Logs After Redeploy:

**Working:**
```
✅ DATABASE_URL found in environment (length: 85)
Database URL: postgresql+psycopg://***:***@xxxxx.railway.app:5432/railway
```

**Not Working:**
```
⚠️  DATABASE_URL appears to be an unresolved Railway reference: ${{ Postgres.DATABASE_URL }}
⚠️  No DATABASE_URL found, using default: postgresql+psycopg://...
⚠️  Using default localhost database URL
```

---

## Common Issues

### "Service name doesn't match"

**Fix:** Railway service names are case-sensitive and exact. Check the actual service name in Railway dashboard.

### "Variable reference not resolving"

**Fix:** Use "Connect Service" instead - it's more reliable than variable references.

### "I connected but still not working"

**Fix:**
1. Wait 2-3 minutes for Railway to sync
2. Refresh Variables page
3. Check both services have the connection
4. Redeploy backend
5. Check logs for the actual URL being used

---

## 🎯 Recommended Approach

**Use "Connect Service"** (Solution 1) - it's the most reliable method and is what Railway recommends for service-to-service connections.

---

**After fixing, your logs should show the Railway database URL, not localhost!** ✅

