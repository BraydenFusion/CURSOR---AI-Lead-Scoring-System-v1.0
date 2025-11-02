# 🚂 Railway Quick Start Guide

## 🎯 5-Minute Railway Deployment

Fast-track guide to get your Lead Scoring System on Railway.

---

## ✅ Prerequisites Checklist

- [x] Code pushed to GitHub
- [x] Railway account (https://railway.app)
- [ ] SECRET_KEY generated

**Generate SECRET_KEY:**
```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

---

## 🚀 Deployment Steps

### 1. Create Railway Project (2 min)

1. Go to https://railway.app/new
2. Click **"Deploy from GitHub repo"**
3. Select: `BraydenFusion/CURSOR---AI-Lead-Scoring-System-v1.0`
4. Railway will auto-detect `backend/railway.json` and create backend service

### 2. Add PostgreSQL Database (1 min)

1. Click **+ New** → **Database** → **PostgreSQL**
2. Railway auto-creates database
3. Click **Connect** → Select your backend service
4. `DATABASE_URL` is now automatically set!

### 3. Configure Backend (2 min)

**Go to backend service → Variables:**

Add these:
```
SECRET_KEY=<paste-your-generated-key>
ALLOWED_ORIGINS=https://placeholder.railway.app
ENVIRONMENT=production
DEBUG=False
```

*(Update ALLOWED_ORIGINS after frontend deploys)*

### 4. Deploy Backend (2-3 min)

1. Railway auto-deploys when you save variables
2. Wait for deployment to complete (green checkmark)
3. Click **Settings** → **Public Networking** → **Generate Domain**
4. **Copy the URL** (e.g., `https://backend-xxxx.up.railway.app`)

### 5. Add Frontend Service (2 min)

1. Click **+ New** → **GitHub Repo**
2. Select **same repository** again
3. Go to **Settings**
4. Set **Root Directory:** `lead-scoring-system/frontend`
5. Railway should auto-detect from `frontend/railway.json`

### 6. Configure Frontend (1 min)

**Go to frontend service → Variables:**

Add:
```
VITE_API_URL=https://your-backend-url.up.railway.app/api
```

*(Replace with your actual backend URL from step 4)*

### 7. Deploy Frontend (2-3 min)

1. Railway auto-deploys
2. Wait for completion
3. Go to **Settings** → **Public Networking** → **Generate Domain**
4. **Copy the frontend URL**

### 8. Update Backend CORS (1 min)

**Go back to backend service → Variables:**

Update:
```
ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app
```

Click **Redeploy** on backend.

### 9. Run Migrations (2 min)

**Install Railway CLI:**
```bash
npm install -g @railway/cli
railway login
```

**Link and migrate:**
```bash
cd lead-scoring-system/backend
railway link
railway run alembic upgrade head
railway run python create_test_users.py
```

**Or use helper:**
```bash
cd lead-scoring-system
./railway-commands.sh setup
./railway-commands.sh login
cd backend && railway link
cd .. && ./railway-commands.sh migrate
./railway-commands.sh users
```

### 10. Test! (1 min)

1. Visit frontend URL
2. Login: `admin` / `admin123`
3. ✅ You're live!

---

## 📋 Environment Variables Summary

### Backend Variables

```
SECRET_KEY=<64-char-hex-string>
ALLOWED_ORIGINS=https://your-frontend.railway.app
ENVIRONMENT=production
DEBUG=False
```

### Frontend Variables

```
VITE_API_URL=https://your-backend.railway.app/api
```

### Auto-Set by Railway

- `DATABASE_URL` (PostgreSQL)
- `REDIS_URL` (Redis, if added)
- `PORT`
- `RAILWAY_ENVIRONMENT`
- `RAILWAY_PROJECT_ID`

---

## ✅ Verification

After deployment, test these URLs:

1. **Backend Health:** `https://your-backend.railway.app/health`
   - Should return: `{"status": "healthy", "environment": "production"}`

2. **API Docs:** `https://your-backend.railway.app/docs`
   - Should show Swagger UI

3. **Frontend:** `https://your-frontend.railway.app`
   - Should show login page

---

## 🐛 Quick Troubleshooting

### Backend won't start
- Check logs in Railway dashboard
- Verify `SECRET_KEY` is set
- Check `DATABASE_URL` is connected

### Frontend can't connect
- Verify `VITE_API_URL` is correct
- Check CORS includes frontend URL
- Both must use HTTPS

### Migrations fail
```bash
railway run python -c "from app.database import engine; engine.connect(); print('OK')"
```

---

## 📚 Full Documentation

For detailed instructions, see:
- **Complete Guide:** `RAILWAY_DEPLOYMENT.md`
- **Environment Variables:** `RAILWAY_ENV_VARS.md`
- **CLI Commands:** `./railway-commands.sh help`

---

## 💰 Cost Estimate

- **Hobby Plan:** $5/month (includes $5 credit)
- **Estimated:** ~$7/month total
- **Out of pocket:** ~$2/month

---

**Ready to deploy! Follow the steps above.** 🚀

