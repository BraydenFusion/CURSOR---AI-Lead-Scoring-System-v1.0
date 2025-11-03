# ✅ Backend URL Configuration - You Already Have It!

## Your Backend URL

Based on what you said, your backend URL is:
```
https://cursor-ai-lead-scoring-system-v10-production.up.railway.app
```

**This is the base URL** - you just add `/api` to it for API endpoints!

---

## ✅ Quick Fix (2 Minutes)

### Step 1: Set Frontend Environment Variable

1. **Go to Railway Dashboard**
2. **Click Frontend Service** (not backend)
3. **Go to Variables tab**
4. **Add/Update this variable:**
   - **Variable Name:** `VITE_API_URL`
   - **Value:** `https://cursor-ai-lead-scoring-system-v10-production.up.railway.app/api`
   - ⚠️ **Important:** Must include `/api` at the end!

5. **Click "Add" or "Update"**
6. **Railway will auto-redeploy** (wait 2-3 minutes)

### Step 2: Set Backend CORS (If Not Already Set)

1. **Go to Railway Dashboard**
2. **Click Backend Service**
3. **Go to Variables tab**
4. **Add/Update this variable:**
   - **Variable Name:** `ALLOWED_ORIGINS`
   - **Value:** `https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app`
   - ⚠️ **Important:** Use your frontend URL (the one you can access)
   - ⚠️ **Important:** No trailing slash

5. **Click "Add" or "Update"**
6. **Railway will auto-redeploy** (wait 2-3 minutes)

---

## 🧪 Test Before Setting Variables

### Test Backend API Endpoint:
Open this in your browser:
```
https://cursor-ai-lead-scoring-system-v10-production.up.railway.app/api/auth/login
```

**Expected:**
- Should show an error about missing credentials (this is OK - means endpoint exists!)
- OR might show HTML/CORS error (will fix after setting variables)

### Test Backend Health:
```
https://cursor-ai-lead-scoring-system-v10-production.up.railway.app/health
```

**Expected:**
```json
{
  "status": "healthy",
  "environment": "production",
  ...
}
```

---

## 📋 Summary

**Your Configuration:**

| Service | URL | Variable to Set |
|---------|-----|----------------|
| **Backend Base** | `https://cursor-ai-lead-scoring-system-v10-production.up.railway.app` | (Base URL) |
| **Backend API** | `https://cursor-ai-lead-scoring-system-v10-production.up.railway.app/api` | `VITE_API_URL` |
| **Frontend** | `https://cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app` | `ALLOWED_ORIGINS` |

---

## ✅ After Setting Variables

1. **Wait 2-3 minutes** for Railway to redeploy
2. **Refresh your frontend page**
3. **Open browser console** (F12 → Console)
4. **Look for:** `🔗 AuthContext API Base URL: https://cursor-ai-lead-scoring-system-v10-production.up.railway.app/api`
5. **Try logging in** with `admin` / `admin123`

**It should work now!** 🎉

---

## 🐛 If Still Not Working

**Check these:**

1. **Console still shows localhost?**
   - `VITE_API_URL` not set correctly or not redeployed yet
   - Check Variables tab, ensure value is exactly: `https://cursor-ai-lead-scoring-system-v10-production.up.railway.app/api`

2. **CORS error?**
   - `ALLOWED_ORIGINS` not set or wrong
   - Ensure it matches your frontend URL exactly

3. **404 error?**
   - Backend endpoint might not exist
   - Verify backend is running (check deploy logs)

4. **500 error?**
   - Backend has an error
   - Check backend deploy logs for errors
   - Verify database is connected

---

**Set those two variables and you should be good to go!** 🚀

