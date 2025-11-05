# Railway URLs Configuration Guide

## ✅ Correct URLs for Your Project

Based on your Railway deployment:

### Backend Service
- **Service Name:** BACKEND
- **Public URL:** `https://backend-base.up.railway.app`
- **API Base URL:** `https://backend-base.up.railway.app/api`

### Frontend Service
- **Service Name:** FRONTEND
- **Public URL:** `https://frontend-production-e9b2.up.railway.app`

### Database Service
- **Service Name:** DATABASE
- **Internal Connection:** Automatically configured via Railway Reference Variables
- **No public URL needed** (internal only)

---

## 🔧 Required Environment Variables

### Frontend Service Variables

**Variable Name:** `VITE_API_URL`  
**Variable Value:** `https://backend-base.up.railway.app/api`

**Important:** 
- ✅ MUST include `/api` suffix
- ✅ Use `https://` protocol
- ✅ No trailing slash after `/api`

**Where to set:**
1. Railway Dashboard → FRONTEND service
2. Variables tab
3. Set `VITE_API_URL` = `https://backend-base.up.railway.app/api`

---

### Backend Service Variables

**Variable Name:** `API_URL` (optional, not required)  
**Variable Value:** `https://backend-base.up.railway.app/api`

**Note:** This variable is optional. The backend doesn't need to know its own URL. You can remove it if you want.

**Required Backend Variables:**
- ✅ `DATABASE_URL` - Automatically set via Railway Reference Variables
- ✅ `SECRET_KEY` - JWT signing key
- ✅ `ENVIRONMENT` - Set to `production`
- ✅ `ALLOWED_ORIGINS` or `CORS_ORIGINS` - Should include frontend URL

---

## ✅ Verification Checklist

### 1. Frontend Configuration
- [ ] `VITE_API_URL` is set to `https://backend-base.up.railway.app/api`
- [ ] No trailing slash after `/api`
- [ ] Frontend service is deployed and active

### 2. Backend Configuration
- [ ] CORS allows `https://frontend-production-e9b2.up.railway.app`
- [ ] Backend service is deployed and active
- [ ] Database connection is working (check `/health` endpoint)

### 3. Test Connection

**Test Backend Health:**
```bash
curl https://backend-base.up.railway.app/health
```

**Test API Config Endpoint:**
```bash
curl https://backend-base.up.railway.app/api/config
```

**Test CORS (from frontend domain):**
```bash
curl -H "Origin: https://frontend-production-e9b2.up.railway.app" \
     -H "Access-Control-Request-Method: POST" \
     -X OPTIONS \
     https://backend-base.up.railway.app/api/auth/login
```

---

## 🐛 Common Issues

### Issue: Frontend can't connect to backend

**Symptom:** Error message: "Cannot connect to backend at https://..."

**Solutions:**
1. ✅ Verify `VITE_API_URL` includes `/api` suffix
2. ✅ Clear browser cache and hard refresh
3. ✅ Check browser console (F12) for actual URL being used
4. ✅ Verify backend is running (check Railway dashboard)

### Issue: CORS errors

**Symptom:** Browser console shows CORS errors

**Solutions:**
1. ✅ Verify backend CORS includes frontend URL
2. ✅ Check backend logs for CORS configuration
3. ✅ Ensure `https://frontend-production-e9b2.up.railway.app` is in allowed origins

---

## 📝 Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | `https://frontend-production-e9b2.up.railway.app` | User-facing web app |
| Backend API | `https://backend-base.up.railway.app/api` | API endpoints |
| Backend Health | `https://backend-base.up.railway.app/health` | Health check |
| Backend Docs | `https://backend-base.up.railway.app/docs` | API documentation |

---

## 🔄 After Making Changes

1. **Redeploy Services:**
   - Changes to environment variables trigger automatic redeploy
   - Or manually trigger redeploy from Railway dashboard

2. **Clear Browser Cache:**
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or use incognito/private window

3. **Verify in Browser Console:**
   - Open DevTools (F12) → Console
   - Look for: `🔗 AuthContext API Base URL: https://backend-base.up.railway.app/api`
   - Should match your configured URL exactly

