# 🔗 Connect Frontend to Backend on Railway

## ✅ Current Status
- ✅ Frontend deployed and accessible
- ✅ Login page loads
- ⚠️ Need to connect frontend to backend API

## 📋 Steps to Connect Frontend to Backend

### Step 1: Get Your Backend URL (2 min)

1. Go to Railway Dashboard
2. Click on your **Backend Service**
3. Go to **Settings** tab
4. Scroll to **"Public Networking"** section
5. **Copy your backend domain** (e.g., `https://backend-production-abc123.up.railway.app`)

**Save this URL!**

### Step 2: Set Frontend Environment Variable (2 min)

1. Go to Railway Dashboard
2. Click on your **Frontend Service**
3. Go to **Variables** tab
4. Look for `VITE_API_URL` variable:
   - **If it exists:** Click to edit it
   - **If it doesn't exist:** Click **"+ New Variable"**

5. Set the value:
   - **Variable Name:** `VITE_API_URL`
   - **Value:** `https://your-backend-url.railway.app/api`
   - ⚠️ **IMPORTANT:** Replace `your-backend-url` with your actual backend domain
   - ⚠️ **IMPORTANT:** Must include `/api` at the end
   - ⚠️ **IMPORTANT:** Must use `https://`

**Example:**
```
VITE_API_URL=https://backend-production-abc123.up.railway.app/api
```

6. Click **"Add"** or **"Update"** to save

### Step 3: Update Backend CORS (2 min)

1. Go back to **Backend Service** → **Variables** tab
2. Find `ALLOWED_ORIGINS` variable:
   - **If it exists:** Click to edit it
   - **If it doesn't exist:** Click **"+ New Variable"**

3. Set the value:
   - **Variable Name:** `ALLOWED_ORIGINS`
   - **Value:** `https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app`
   - ⚠️ **IMPORTANT:** Use your actual frontend URL (the one that works)
   - ⚠️ **IMPORTANT:** Must use `https://`
   - ⚠️ **IMPORTANT:** No trailing slash

**Example:**
```
ALLOWED_ORIGINS=https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app
```

4. Click **"Add"** or **"Update"** to save

### Step 4: Redeploy Services (3 min)

Both services will auto-redeploy after you save variables, but you can also:

1. **Frontend Service:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** (optional - auto-redeploys on variable change)

2. **Backend Service:**
   - Go to **Deployments** tab
   - Click **"Redeploy"** (optional - auto-redeploys on variable change)

Wait 2-3 minutes for redeployment.

### Step 5: Test the Connection (2 min)

1. **Open your frontend URL:**
   ```
   https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app
   ```

2. **Open browser DevTools** (F12 or Right-click → Inspect)
   - Go to **Console** tab
   - Look for: `API Base URL: https://your-backend-url.railway.app/api`
   - This confirms the environment variable is loaded

3. **Try to login:**
   - Enter username: `admin`
   - Enter password: `admin123`
   - Click **"Sign In"**

4. **Check for errors:**
   - ✅ **Success:** Should redirect to dashboard
   - ❌ **CORS Error:** Backend CORS not configured correctly
   - ❌ **404/Network Error:** Backend URL incorrect or backend not running
   - ❌ **500 Error:** Backend issue (check backend logs)

## 🔍 Troubleshooting

### Issue: "API Base URL: http://localhost:8000/api" in Console
**Fix:** `VITE_API_URL` environment variable not set or not loaded
- Check Railway Variables tab
- Ensure variable name is exactly `VITE_API_URL`
- Redeploy frontend after adding variable

### Issue: CORS Error in Browser
**Fix:** Backend CORS not configured
- Verify `ALLOWED_ORIGINS` in backend variables
- Ensure frontend URL is correct (no trailing slash)
- Redeploy backend after updating CORS

### Issue: Network Error or 404
**Fix:** Backend URL incorrect
- Verify backend domain in Railway Settings → Public Networking
- Ensure `VITE_API_URL` ends with `/api`
- Check backend is running (check backend deploy logs)

### Issue: 500 Error on Login
**Fix:** Backend database connection issue
- Check backend deploy logs
- Ensure database is connected (from earlier steps)
- Verify `DATABASE_URL` is set in backend

## ✅ Success Checklist

After setup:
- [ ] `VITE_API_URL` set in frontend variables
- [ ] `ALLOWED_ORIGINS` set in backend variables
- [ ] Frontend redeployed
- [ ] Backend redeployed
- [ ] Console shows correct API Base URL
- [ ] Login works (no CORS errors)
- [ ] Dashboard loads after login

## 🎉 Once Connected

Your full-stack application will be:
- ✅ Frontend accessible via Railway URL
- ✅ Backend API accessible
- ✅ Frontend communicates with backend
- ✅ Authentication working
- ✅ CORS properly configured

You'll be able to test the complete application! 🚀

