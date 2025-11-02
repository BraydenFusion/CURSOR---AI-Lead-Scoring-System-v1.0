# Railway Environment Variables

Quick reference for setting environment variables in Railway.

---

## Backend Service

Copy these to Railway Dashboard → Backend Service → Variables:

### Required

```
SECRET_KEY=<GENERATE_NEW_KEY_HERE>
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
ENVIRONMENT=production
DEBUG=False
```

### Generate SECRET_KEY

Run this command locally:

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and paste as `SECRET_KEY` value.

---

### Optional (Email Notifications)

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-gmail-app-password
FROM_EMAIL=noreply@leadscoring.com
```

**Note:** For Gmail, you need to create an "App Password":
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Create App Password
4. Use that as `SMTP_PASSWORD`

---

### Automatic (Set by Railway)

These are set automatically when you add services:

- `DATABASE_URL` - Set by PostgreSQL service (when connected)
- `REDIS_URL` - Set by Redis service (when connected)
- `PORT` - Set by Railway automatically
- `RAILWAY_ENVIRONMENT` - Set by Railway
- `RAILWAY_PROJECT_ID` - Set by Railway

**Do NOT set these manually!**

---

## Frontend Service

Copy these to Railway Dashboard → Frontend Service → Variables:

### Required

```
VITE_API_URL=https://your-backend.up.railway.app/api
```

**Replace `your-backend.up.railway.app` with your actual backend URL**

**Important:**
- Use HTTPS
- Include `/api` at the end
- No trailing slash after `/api`

---

## Setup Order

1. **Deploy backend first** (to get the backend URL)
2. **Get backend URL** from Railway dashboard
3. **Set frontend `VITE_API_URL`** with backend URL
4. **Set backend `ALLOWED_ORIGINS`** with frontend URL (after frontend deploys)
5. **Redeploy both services**

---

## Example Values

### Backend Variables

```
SECRET_KEY=a1b2c3d4e5f6...64-char-hex-string
ALLOWED_ORIGINS=https://frontend-production-abc123.up.railway.app
ENVIRONMENT=production
DEBUG=False
```

### Frontend Variables

```
VITE_API_URL=https://backend-production-xyz789.up.railway.app/api
```

---

## Verification

After setting variables:

1. **Backend:** Visit `https://your-backend.railway.app/health`
   - Should return: `{"status": "healthy", "environment": "production"}`

2. **Frontend:** Visit `https://your-frontend.railway.app`
   - Should load login page
   - Check browser console for API connection

---

## Troubleshooting

### "SECRET_KEY not set"
- Make sure you set it in backend service Variables
- Redeploy backend after adding

### CORS errors
- Check `ALLOWED_ORIGINS` includes exact frontend URL
- Must use HTTPS
- No trailing slash
- Redeploy backend after updating

### Frontend can't connect
- Check `VITE_API_URL` is correct
- Must include `/api`
- Check backend is accessible: `curl https://your-backend.railway.app/health`

---

**Quick Copy Template:**

Backend:
```
SECRET_KEY=
ALLOWED_ORIGINS=
ENVIRONMENT=production
DEBUG=False
```

Frontend:
```
VITE_API_URL=
```

