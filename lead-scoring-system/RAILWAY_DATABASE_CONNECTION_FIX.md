# 🔧 Railway Database Connection Fix

## Problem
Your app is trying to connect to `localhost:5433` instead of Railway's database, which means `DATABASE_URL` is not set.

**Error:**
```
connection to server at "127.0.0.1", port 5433 failed: Connection refused
```

---

## Solution: Connect PostgreSQL to Backend Service

### Step 1: Verify PostgreSQL Service Exists

1. Go to Railway Dashboard
2. Check if you have a **PostgreSQL** service in your project
3. If not, add one:
   - Click **"+ New"**
   - Select **"Database"** → **"PostgreSQL"**

### Step 2: Connect Database to Backend

1. Click on your **PostgreSQL service**
2. Go to **"Connect"** tab (or **"Variables"** tab)
3. Click **"Connect Service"** button
4. **Select your Backend service** from the dropdown
5. Railway will automatically:
   - Set `DATABASE_URL` environment variable in your backend
   - Make the database accessible to your backend

### Step 3: Verify Connection

After connecting:

1. Go to **Backend Service** → **Variables** tab
2. Look for `DATABASE_URL` environment variable
3. It should look like: `postgres://postgres:xxxxx@xxxxx.railway.app:5432/railway`

**If you don't see `DATABASE_URL`:**
- The services aren't connected yet
- Go back to Step 2 and ensure you clicked "Connect Service"

### Step 4: Redeploy Backend

Once `DATABASE_URL` is set:

1. Go to Backend Service → **Deployments**
2. Click **"Redeploy"** button
3. Wait for deployment to complete

### Step 5: Check Logs

After redeployment, check logs:

**Should see:**
```
Database URL: postgresql+psycopg://***:***@xxxxx.railway.app:5432/railway
```

**Should NOT see:**
```
⚠️  Using default localhost database URL
```

---

## Alternative: Set DATABASE_URL Manually

If connecting services doesn't work:

1. Go to PostgreSQL service → **Variables** tab
2. Find `DATABASE_URL` or `PGDATABASE`
3. Copy the value
4. Go to Backend service → **Variables** tab
5. Click **"+ New Variable"**
6. Name: `DATABASE_URL`
7. Value: Paste the URL from PostgreSQL
8. Click **"Add"**
9. Redeploy backend

---

## Verify Database Connection

After redeploy, test with:

```bash
curl https://your-backend.railway.app/health
```

If successful, try login again in Postman.

---

## Expected Database URL Format

Railway's `DATABASE_URL` typically looks like:
```
postgres://postgres:password@containers-us-west-xxx.railway.app:5432/railway
```

The config automatically converts `postgres://` to `postgresql+psycopg://` for SQLAlchemy.

---

## Troubleshooting

### Still connecting to localhost?

1. **Check environment variables:**
   - Backend → Variables → Verify `DATABASE_URL` exists
   - If missing, connect services again (Step 2)

2. **Check logs:**
   - Should show masked database URL
   - Should NOT show localhost warning

3. **Force redeploy:**
   - Backend → Deployments → Redeploy

### "Connection refused" even with correct URL?

1. **Wait a moment:**
   - Railway database takes 1-2 minutes to be ready after connection

2. **Check PostgreSQL service:**
   - Make sure it's running (not paused)
   - Should show "Active" status

3. **Check firewall:**
   - Railway handles this automatically when services are connected
   - No manual configuration needed

---

**Once DATABASE_URL is set correctly, your login should work!** ✅

