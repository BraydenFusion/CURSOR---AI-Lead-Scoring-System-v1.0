# Railway Backend URL Configuration

## Problem
The frontend cannot connect to the backend, showing error:
```
Network error: Cannot connect to backend at https://backend-production-e9b2.up.railway.app/api
```

## Solution: Set Backend URL Environment Variable

### Option 1: Set Environment Variable in Railway (Recommended)

1. **Go to Railway Dashboard**
   - Navigate to your project
   - Click on the **FRONTEND** service

2. **Add Environment Variable**
   - Click on the **Variables** tab
   - Click **+ New Variable**
   - Add:
     - **Variable Name:** `VITE_API_URL`
     - **Value:** `https://backend-base.up.railway.app/api` 
       (Replace with your actual backend URL - check the BACKEND service for the correct URL)
   - Click **Add**

3. **Redeploy Frontend**
   - After adding the variable, Railway will automatically redeploy
   - Or manually trigger a redeploy from the Deployments tab

### Option 2: Find Your Backend URL

1. **Check Backend Service URL**
   - In Railway Dashboard, click on **BACKEND** service
   - Look for the **Public URL** or check the **Settings** tab
   - Common patterns:
     - `https://backend-base.up.railway.app`
     - `https://backend-production-xxx.up.railway.app`
     - `https://your-project-backend-xxx.up.railway.app`

2. **Use the Backend URL**
   - The frontend expects the backend URL with `/api` suffix
   - Example: If backend is `https://backend-base.up.railway.app`, set:
     ```
     VITE_API_URL=https://backend-base.up.railway.app/api
     ```

### Option 3: Verify Backend is Running

1. **Check Backend Health**
   - Visit: `https://YOUR-BACKEND-URL/health`
   - Should return a JSON response with status

2. **Check Backend Logs**
   - In Railway Dashboard → BACKEND service → Deployments
   - Check the latest deployment logs for errors

3. **Verify CORS Configuration**
   - Backend should allow requests from your frontend domain
   - Check backend logs for CORS errors

## Troubleshooting

### If the error persists:

1. **Check Browser Console**
   - Open DevTools (F12) → Console tab
   - Look for CORS errors or network errors
   - Check what URL the frontend is trying to use

2. **Verify Backend is Accessible**
   ```bash
   curl https://YOUR-BACKEND-URL/health
   ```

3. **Check Railway Service Status**
   - Ensure both FRONTEND and BACKEND services show "Active"
   - Check for any failed deployments

4. **Clear Browser Cache**
   - Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
   - Or use incognito/private window

## Current Configuration

The frontend will now try these backend URLs in order:
1. `VITE_API_URL` environment variable (if set)
2. `backend-base.up.railway.app` (common Railway pattern)
3. `backend-production-xxx.up.railway.app` (inferred from frontend URL)
4. Other inferred patterns

If none work, it will fall back to `http://localhost:8000/api` (development).

