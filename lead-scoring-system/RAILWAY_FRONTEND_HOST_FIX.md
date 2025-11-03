# 🔧 Fix Railway Frontend Host Blocking Issue

## Issue
When accessing the frontend via Railway domain, getting error:
```
Blocked request. This host ("cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app") is not allowed.
To allow this host, add "cursor-ai-lead-scoring-system-v10-production-8d7f.up.railway.app" to `preview.allowedHosts` in vite.config.js.
```

## Root Cause
Vite's preview mode (used by `npm run preview`) has host checking enabled by default for security. Railway provides dynamic hostnames, so we need to configure Vite to allow all hosts.

## ✅ Fix Applied

**File:** `frontend/vite.config.ts`

Added `preview` configuration:
```typescript
preview: {
  port: parseInt(process.env.PORT || "5173"),
  host: "0.0.0.0",
  allowedHosts: ["all"], // Allow all hosts for Railway
}
```

### What This Does:
- **`host: "0.0.0.0"`** - Listen on all network interfaces (required for Railway)
- **`allowedHosts: ["all"]`** - Allow any hostname (needed because Railway hostnames are dynamic)
- **`port: process.env.PORT`** - Use Railway's PORT environment variable

## 🚀 After Fix

1. **Changes will be pushed to GitHub**
2. **Railway will auto-redeploy**
3. **Frontend should now work** when accessed via Railway domain

## ⚠️ Security Note

Allowing all hosts is safe in this context because:
- Railway handles HTTPS/TLS
- Railway provides secure hostnames
- Preview mode is only used in production deployment
- The application doesn't rely on hostname checking for security

## ✅ Test After Deployment

1. Wait for Railway to redeploy (2-3 minutes)
2. Access your frontend URL
3. Should load without host blocking error
4. Should display the login page

If you still see issues, check Railway deploy logs for any errors.

