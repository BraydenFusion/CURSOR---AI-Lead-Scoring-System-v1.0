# 🚨 URGENT: Connect PostgreSQL to Backend in Railway

## Current Problem
Backend is trying to connect to `127.0.0.1:5433` (localhost) instead of Railway's PostgreSQL database.

**Error:** `connection to server at "127.0.0.1", port 5433 failed: Connection refused`

**Cause:** PostgreSQL service is not connected to Backend service in Railway, so `DATABASE_URL` is not set.

---

## ✅ Solution: Connect PostgreSQL Service (5 Minutes)

### Step 1: Find PostgreSQL Service

1. **Go to Railway Dashboard:** https://railway.app
2. **Open your project**
3. **Look for a service named:**
   - "Postgres" 
   - "PostgreSQL"
   - "Database"
   - OR a service with a database icon

**If you don't see one:**
- Click **"+ New"** button (top right)
- Select **"Database"** → **"PostgreSQL"**
- Wait 30 seconds for it to create

### Step 2: Connect PostgreSQL to Backend

**Option A: Using "Connect Service" (Recommended)**

1. **Click on your PostgreSQL service**
2. **Look for one of these tabs:**
   - **"Connect"** tab
   - **"Variables"** tab  
   - **"Settings"** tab
3. **Find the "Connect Service" button** (or "Add Service" or "Link Service")
   - It might be at the top of the page
   - Or in a dropdown menu
   - Or in the Variables tab
4. **Click "Connect Service"** (or similar button)
5. **A dropdown/modal will appear** - select your **Backend service**
   - It might be named "Backend", "API", "Server", or similar
6. **Click "Connect"** or "Add"
7. **Railway will automatically set `DATABASE_URL`** in your backend service!

**Option B: If "Connect Service" Button Not Found**

Some Railway interfaces show it differently:

1. **PostgreSQL Service → Variables tab**
2. **Look for:** "Connected Services" section
3. **Or:** "Share Variables" section
4. **Find:** Button to share `DATABASE_URL` with other services
5. **Select:** Your Backend service
6. **Enable:** Variable sharing for `DATABASE_URL`

### Step 3: Verify DATABASE_URL is Set

1. **Go to Backend Service** (not PostgreSQL)
2. **Click "Variables" tab**
3. **Look for `DATABASE_URL`** variable
   - Should be automatically added by Railway
4. **Value should look like:**
   ```
   postgres://postgres:xxxxx@xxxxx.railway.app:5432/railway
   ```
   OR
   ```
   postgresql://postgres:xxxxx@xxxxx.railway.app:5432/railway
   ```

**✅ If you see `DATABASE_URL`:** You're good! Skip to Step 5.

**❌ If you DON'T see `DATABASE_URL`:** 
- Go back to Step 2 and try the connection again
- Or try Option C below

### Step 4: Manual Setup (If Connect Doesn't Work)

If "Connect Service" doesn't work or `DATABASE_URL` doesn't appear:

1. **Go to PostgreSQL Service → Variables tab**
2. **Find `DATABASE_URL`** (or `PGDATABASE`)
3. **Click to reveal the value** (eye icon or click to expand)
4. **Copy the ENTIRE URL**
5. **Go to Backend Service → Variables tab**
6. **Click "+ New Variable"**
7. **Set:**
   - **Name:** `DATABASE_URL`
   - **Value:** Paste the URL you copied
8. **Click "Add"**
9. **Redeploy backend** (will auto-redeploy)

### Step 5: Redeploy Backend

1. **Go to Backend Service → Deployments tab**
2. **Click "Redeploy"** (or wait for auto-redeploy if you just set variables)
3. **Wait 2-3 minutes** for deployment

### Step 6: Check Backend Deploy Logs

After redeploy, check **Deploy Logs** tab:

**✅ SUCCESS - You should see:**
```
✅ DATABASE_URL found in environment (length: XX)
Database URL: postgresql+psycopg://***:***@xxxxx.railway.app:5432/railway
```

**❌ FAILURE - If you still see:**
```
⚠️  No DATABASE_URL found, using default: postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring
⚠️  Using default localhost database URL
```

**If still failing:**
- `DATABASE_URL` is not set correctly
- Go back to Step 2 or Step 4
- Double-check the variable name is exactly `DATABASE_URL`
- Ensure the value is the full PostgreSQL URL from Railway

### Step 7: Test Login Again

1. **Wait for backend to fully deploy** (check logs show "Application startup complete")
2. **Go to your frontend:** `https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app`
3. **Try logging in** with: `admin` / `admin123`

**Expected:**
- ✅ Should work now (if users exist)
- ❌ If "Incorrect username or password" → Users need to be created (next step)

---

## 🔄 If You Still See Database Errors

### Check These:

1. **Backend Deploy Logs:**
   - Look for the database URL warning messages
   - Check if `DATABASE_URL` is being logged

2. **Backend Variables:**
   - Ensure `DATABASE_URL` exists
   - Ensure it's not a variable reference `${{ }}`
   - Ensure it's the actual URL value

3. **PostgreSQL Service:**
   - Ensure PostgreSQL service is running (check deploy logs)
   - Ensure it's in the same Railway project

4. **Service Connection:**
   - Verify services are "connected" in Railway
   - Some Railway interfaces show connection status

---

## 📋 Quick Checklist

- [ ] Found PostgreSQL service in Railway
- [ ] Connected PostgreSQL to Backend (using "Connect Service")
- [ ] Verified `DATABASE_URL` appears in Backend → Variables
- [ ] Backend redeployed
- [ ] Deploy logs show Railway database URL (not localhost)
- [ ] Test login works

---

## 🎯 After Database is Connected

Once `DATABASE_URL` is set and backend connects:

1. **Create test users** (if not already done)
2. **Test login** with `admin` / `admin123`
3. **Should work!** ✅

---

**The key step is connecting the PostgreSQL service to the Backend service in Railway using "Connect Service" - this automatically sets `DATABASE_URL`!** 🚀

