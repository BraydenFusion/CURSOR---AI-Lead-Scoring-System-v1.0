# 🔗 Railway Services Connection Guide

## Understanding Railway Service Connections

### Important: HTTP Services Don't Need Explicit Connections

Unlike database connections, **HTTP services (Frontend ↔ Backend) don't need explicit "connections" in Railway's Architecture view**. They communicate via URLs over the internet.

### What You See in Architecture View

**✅ Backend ↔ Database Connection:**
- Shows a **dashed arrow** connection
- This is because the backend uses Railway's **internal networking** to connect to the database
- Uses `DATABASE_URL` with internal hostname like `postgres.railway.internal`
- This is a **service-to-service connection** using Railway's internal network

**❌ Frontend ↔ Backend Connection:**
- **No connection arrow shown** - this is **NORMAL and EXPECTED**
- Frontend and Backend communicate via **public HTTP URLs**
- Frontend calls: `https://backend-production-e9b2.up.railway.app/api/auth/login`
- Backend responds with CORS headers allowing the frontend domain
- This is **standard web architecture** - no special connection needed

## Why No Connection Arrow?

Railway's Architecture view shows:
- **Internal service connections** (like database connections using Railway's internal network)
- **NOT external HTTP connections** (like frontend calling backend via public URLs)

This is by design - HTTP services are independent and communicate via URLs, not internal service links.

## VITE_API_URL Variable

### ✅ You DON'T Need to Set VITE_API_URL

The frontend now **automatically detects** the backend URL:
1. Detects Railway environment by checking hostname
2. Infers backend URL from frontend URL pattern
3. Example: `frontend-production-xxx` → `backend-production-xxx`

### Optional: Manual Configuration

If you want to **explicitly set** the backend URL (optional):

1. **In Railway Dashboard:**
   - Go to **Frontend Service** → **Variables** tab
   - Click **"+ New Variable"**
   - Name: `VITE_API_URL`
   - Value: `https://backend-production-e9b2.up.railway.app/api`
   - **Important:** Must be set **BEFORE** building (Vite env vars are embedded at build time)

2. **Why Set It?**
   - More explicit control
   - Works if frontend/backend naming doesn't match pattern
   - Useful for debugging

3. **Why NOT Set It?**
   - Auto-detection works automatically
   - No manual configuration needed
   - Adapts to Railway domain changes

## Current Status Check

### ✅ What's Working

1. **Backend URL Detection:**
   - Frontend correctly detects: `https://backend-production-e9b2.up.railway.app/api`
   - Console shows: `API Base URL: https://backend-production-e9b2.up.railway.app/api`

2. **CORS Configuration:**
   - Backend allows: `https://frontend-production-e9b2.up.railway.app`
   - Regex pattern allows all Railway domains: `.*\.up\.railway\.app`

3. **Route Registration:**
   - Backend logs verify auth routes are registered
   - `/api/auth/login` endpoint exists

### 🔍 If You Still See Errors

**404 Error:**
- Check Railway Backend → Deploy Logs
- Look for: `✅ Login route found: ['POST'] /api/auth/login`
- If missing, routes aren't registering (check startup errors)

**CORS Error:**
- Check Railway Backend → Deploy Logs
- Look for: `CORS allowed origins: ['https://frontend-production-e9b2.up.railway.app', ...]`
- Verify frontend domain is in the list

**Network Error:**
- Check if backend is actually running
- Visit: `https://backend-production-e9b2.up.railway.app/health`
- Should return JSON with `"status": "healthy"`

## Summary

| Item | Status | Explanation |
|------|--------|-------------|
| Frontend-Backend Connection Arrow | ❌ Not needed | HTTP services communicate via URLs, not internal connections |
| VITE_API_URL Variable | ⚠️ Optional | Auto-detection works, but you can set it manually if needed |
| Backend-Database Connection Arrow | ✅ Present | Internal service connection using Railway networking |
| CORS Configuration | ✅ Fixed | Backend allows Railway frontend domains |
| Route Registration | ✅ Verified | Logs show auth routes are registered |

## Next Steps

1. **No action needed** for the missing connection arrow - this is normal
2. **No action needed** for VITE_API_URL - auto-detection is working
3. **If errors persist:**
   - Check Railway Backend deploy logs for route verification
   - Verify CORS configuration includes your frontend domain
   - Test backend health: `https://backend-production-e9b2.up.railway.app/health`

---

**Key Takeaway:** The missing connection arrow between Frontend and Backend is **normal and expected**. HTTP services don't need explicit connections in Railway - they communicate via public URLs.

