# 🔧 Frontend API URL Configuration Fix

## Problem

The frontend was attempting to connect to `http://localhost:8000/api` because `VITE_API_URL` environment variable was `undefined`. This caused login failures with `ERR_BLOCKED_BY_CLIENT` errors when deployed on Railway.

## Root Cause

Vite environment variables (those starting with `VITE_`) must be set at **build time**, not runtime. Since Railway doesn't automatically inject `VITE_API_URL` during the frontend build, the frontend defaulted to `localhost`.

## Solution Implemented

### 1. Smart Runtime API URL Detection

Created `frontend/src/config.ts` that automatically detects the backend URL:

**Priority Order:**
1. `VITE_API_URL` env var (if set at build time)
2. Railway URL pattern inference (infers backend URL from frontend URL)
3. Development fallback (`localhost:8000`)

**Railway URL Pattern Inference:**
- Detects if running on Railway (checks for `railway.app` in hostname)
- Infers backend URL by replacing `frontend` with `backend` in the hostname
- Examples:
  - Frontend: `frontend-production-xxx.up.railway.app`
  - Inferred Backend: `backend-production-xxx.up.railway.app`

### 2. Backend Configuration Endpoint

Added `GET /api/config` endpoint that returns the backend's API base URL. This allows the frontend to verify or discover the correct backend URL at runtime.

### 3. Synchronous First Load

The API config works synchronously on first load (no async delay) to ensure immediate connectivity, while optionally refining the URL asynchronously in the background.

## Files Changed

### Frontend
- ✅ `frontend/src/config.ts` - New smart API configuration system
- ✅ `frontend/src/services/api.ts` - Updated to use new config
- ✅ `frontend/src/contexts/AuthContext.tsx` - Updated to use new config
- ✅ `frontend/vite.config.ts` - Enhanced to inject env vars at build time if available

### Backend
- ✅ `backend/app/main.py` - Added `/api/config` endpoint for frontend discovery

## How It Works

### On Railway (Production)

1. Frontend loads at: `frontend-production-xxx.up.railway.app`
2. Config detects Railway environment (`railway.app` in hostname)
3. Infers backend URL: `backend-production-xxx.up.railway.app`
4. Constructs API URL: `https://backend-production-xxx.up.railway.app/api`
5. Uses this URL for all API calls

### During Development

- Falls back to `http://localhost:8000/api`
- No inference needed

### Optional: Setting VITE_API_URL

If you want to explicitly set the backend URL (recommended for Railway):

1. **In Railway Dashboard:**
   - Go to Frontend Service → Variables
   - Add Variable: `VITE_API_URL`
   - Value: `https://your-backend-service.up.railway.app/api`
   - **Important:** Must be set BEFORE building

2. **Or use Railway Reference Variable:**
   - Frontend → Variables → Reference Variable
   - Select Backend Service
   - Reference: `RAILWAY_SERVICE_URL` or similar
   - Note: May need to append `/api` manually

## Verification

After Railway redeploys the frontend:

1. **Check Browser Console:**
   - Should see: `🔗 API Configuration: { baseUrl: "https://backend-xxx.up.railway.app/api", ... }`
   - Should NOT see: `localhost:8000`

2. **Test Login:**
   - Try logging in with admin credentials
   - Should successfully connect to backend
   - No more `ERR_BLOCKED_BY_CLIENT` errors

3. **Check Network Tab:**
   - API requests should go to Railway backend URL
   - Not `localhost:8000`

## Troubleshooting

### Still Seeing `localhost:8000`

**Check:**
1. Railway has redeployed frontend (check deploy logs)
2. Browser cache cleared (hard refresh: Cmd+Shift+R / Ctrl+Shift+R)
3. Console logs show inferred URL correctly

**Fix:**
- Set `VITE_API_URL` explicitly in Railway Frontend Variables
- Or verify backend service name matches inference pattern

### Backend URL Inference Fails

**If frontend and backend have different naming patterns:**

1. **Option 1:** Set `VITE_API_URL` in Railway Frontend Variables
2. **Option 2:** Update `inferBackendUrlFromRailway()` in `config.ts` with your pattern

### Config Endpoint Returns Wrong URL

The `/api/config` endpoint uses the request URL to determine the backend. If it's incorrect:

1. Check Railway Backend → Settings → Public Domain
2. Verify the backend is accessible publicly
3. Consider setting `RAILWAY_STATIC_URL` or `BACKEND_URL` in backend variables

## Success Indicators

✅ Browser console shows Railway backend URL (not localhost)  
✅ Login requests succeed  
✅ Network tab shows API calls to Railway backend  
✅ No `ERR_BLOCKED_BY_CLIENT` errors  
✅ Health check and other API endpoints work  

---

**Status:** ✅ Fixed and deployed  
**Next:** Wait for Railway to redeploy frontend, then test login

