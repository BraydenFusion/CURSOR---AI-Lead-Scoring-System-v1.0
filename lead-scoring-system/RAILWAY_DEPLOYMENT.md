# Railway Deployment Guide

## 🚀 Quick Deployment Steps

### Prerequisites
- Railway account (https://railway.app)
- GitHub repository with your code
- SECRET_KEY generated

---

## PART 1: BACKEND DEPLOYMENT

### Step 1: Create Railway Project

1. Go to https://railway.app/new
2. Click "Deploy from GitHub repo"
3. Select your repository: `BraydenFusion/CURSOR---AI-Lead-Scoring-System-v1.0`
4. Click "Deploy Now"

### Step 2: Configure Backend Service

**In Railway Dashboard:**

1. Click on the service (will auto-detect from `backend/railway.json`)
2. Go to **Settings**
3. Set **Root Directory:** `lead-scoring-system/backend`
4. Set **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Click **Deploy**

Railway should auto-detect the configuration from `backend/railway.json`.

### Step 3: Add PostgreSQL Database

1. In your Railway project, click **+ New**
2. Select **Database** → **PostgreSQL**
3. Railway automatically creates database
4. Railway automatically sets `DATABASE_URL` environment variable
5. **Important:** Make sure to "Connect" the database to your backend service

### Step 4: Add Redis (Optional)

1. Click **+ New**
2. Select **Database** → **Redis**
3. Railway automatically sets `REDIS_URL` environment variable
4. "Connect" Redis to your backend service

### Step 5: Set Environment Variables

**Click on backend service → Variables tab**

**Required Variables:**

```
SECRET_KEY=<generate-with-python3 -c "import secrets; print(secrets.token_hex(32))">
ALLOWED_ORIGINS=https://your-frontend.up.railway.app
ENVIRONMENT=production
DEBUG=False
```

**Generate SECRET_KEY:**

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

**Optional (for email notifications):**

```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@leadscoring.com
```

**Note:** Railway automatically sets:
- `DATABASE_URL` (from PostgreSQL service)
- `REDIS_URL` (from Redis service, if added)
- `PORT` (Railway assigns this)
- `RAILWAY_ENVIRONMENT`
- `RAILWAY_PROJECT_ID`

### Step 6: Run Database Migrations

**Install Railway CLI:**

```bash
npm install -g @railway/cli
railway login
cd lead-scoring-system/backend
railway link
```

**Run migrations:**

```bash
railway run alembic upgrade head
```

**Or using the helper script:**

```bash
cd lead-scoring-system
./railway-commands.sh setup
./railway-commands.sh login
./railway-commands.sh link
./railway-commands.sh migrate
```

**Create test users:**

```bash
railway run python create_test_users.py
```

**Or using helper:**

```bash
./railway-commands.sh users
```

### Step 7: Get Backend URL

1. Go to backend service → **Settings**
2. Find **Public Networking**
3. Click **Generate Domain** (if not already generated)
4. Copy the URL (e.g., `https://backend-production-xxxx.up.railway.app`)

**Save this URL - you'll need it for the frontend!**

---

## PART 2: FRONTEND DEPLOYMENT

### Step 1: Create Frontend Service

1. In Railway project, click **+ New** → **GitHub Repo**
2. Select the **same repository** again
3. Railway will create a new service
4. Go to **Settings**
5. Set **Root Directory:** `lead-scoring-system/frontend`
6. Set **Build Command:** `npm install && npm run build`
7. Set **Start Command:** `npm run preview -- --host 0.0.0.0 --port $PORT`

Railway should auto-detect from `frontend/railway.json`.

### Step 2: Set Frontend Environment Variables

**In frontend service → Variables:**

```
VITE_API_URL=https://your-backend-url.up.railway.app/api
```

**Replace `your-backend-url.up.railway.app` with your actual backend URL from Step 7 above!**

### Step 3: Deploy

Railway will automatically:
1. Install dependencies (`npm install`)
2. Build the app (`npm run build`)
3. Start the preview server (`npm run preview`)

### Step 4: Get Frontend URL

1. Go to frontend service → **Settings**
2. Find **Public Networking**
3. Click **Generate Domain**
4. Copy the URL (e.g., `https://frontend-production-xxxx.up.railway.app`)

### Step 5: Update Backend CORS

**Go back to backend service → Variables**

Update `ALLOWED_ORIGINS` with your frontend URL:

```
ALLOWED_ORIGINS=https://your-frontend-url.up.railway.app
```

Click **Redeploy** on backend service to apply changes.

---

## ✅ VERIFICATION

### Test Backend

Visit: `https://your-backend-url.railway.app/health`

**Expected:** 
```json
{
  "status": "healthy",
  "environment": "production"
}
```

### Test API Docs

Visit: `https://your-backend-url.railway.app/docs`

**Expected:** Swagger UI interface

### Test Frontend

Visit: `https://your-frontend-url.railway.app`

**Expected:** Login page loads

### Login Test

- Username: `admin`
- Password: `admin123`

**Expected:** Dashboard loads with leads

---

## 🐛 TROUBLESHOOTING

### Backend won't start

**Check logs in Railway dashboard:**
1. Click on backend service
2. Click **Deployments** tab
3. Click latest deployment
4. View logs

**Common issues:**
- Missing `SECRET_KEY` → Set in Variables
- Database connection failed → Check `DATABASE_URL` is connected
- Port binding error → Railway sets `$PORT` automatically

**Verify database connection:**
```bash
railway run python -c "from app.database import engine; engine.connect(); print('OK')"
```

### Frontend can't connect to backend

**Check:**
1. `VITE_API_URL` is set correctly in frontend Variables
2. CORS: `ALLOWED_ORIGINS` must include frontend URL
3. Both URLs use HTTPS
4. No trailing slash in `VITE_API_URL` (use `/api` not `/api/`)

**Test backend from frontend service:**
```bash
railway run curl https://your-backend-url.railway.app/health
```

### Database migrations failed

**Check connection:**
```bash
railway run python -c "from app.database import engine; engine.connect(); print('OK')"
```

**Run migrations with verbose output:**
```bash
railway run alembic upgrade head --verbose
```

**Check if tables exist:**
```bash
railway run python -c "
from app.database import engine
from sqlalchemy import inspect
inspector = inspect(engine)
print(inspector.get_table_names())
"
```

### Build fails

**Backend build fails:**
- Check `requirements.txt` is in `backend/` directory
- Verify Python version in `runtime.txt`

**Frontend build fails:**
- Check `package.json` is in `frontend/` directory
- Verify Node.js version (Railway uses Node 20 by default)
- Check build logs for specific errors

### CORS errors in browser console

**Symptoms:** `Access-Control-Allow-Origin` errors

**Fix:**
1. Update backend `ALLOWED_ORIGINS` with exact frontend URL
2. Include protocol: `https://your-frontend.railway.app`
3. No trailing slash
4. Redeploy backend service

---

## 💰 ESTIMATED COSTS

**Railway Hobby Plan:** $5/month includes $5 credit

**Estimated usage:**
- Backend: ~$3/month
- PostgreSQL: ~$2/month
- Redis (optional): ~$1/month
- Frontend: ~$1/month

**Total: ~$7/month** (first $5 covered by plan, ~$2 out of pocket)

**Pro Tip:** Monitor usage in Railway dashboard to optimize costs.

---

## 🔒 SECURITY CHECKLIST

Before going live:

- [ ] Generated new SECRET_KEY for production
- [ ] CORS restricted to production domains only (no `*`)
- [ ] DEBUG=False in production
- [ ] Database backups enabled in Railway
- [ ] Changed default user passwords (if using test users)
- [ ] HTTPS enforced (automatic on Railway)
- [ ] Rate limiting enabled (automatic in production mode)
- [ ] Environment variables encrypted (automatic on Railway)

---

## 📝 NOTES

- ✅ Railway automatically provides SSL certificates
- ✅ Database backups are automatic (daily)
- ✅ Services restart automatically on failure
- ✅ Logs are available in Railway dashboard
- ✅ Environment variables are encrypted
- ✅ Zero-downtime deployments with blue-green strategy
- ✅ Automatic health checks

---

## 🔄 UPDATING/DEPLOYING

### Automatic Deployments

Railway automatically deploys when you push to GitHub:
```bash
git push origin main
```

Railway will:
1. Detect the push
2. Build the service
3. Run health checks
4. Deploy to production

### Manual Deploy

```bash
railway up
```

### View Logs

```bash
railway logs
```

Or in Railway dashboard: Service → Deployments → Latest → Logs

---

## 📚 RAILWAY CLI COMMANDS

See `railway-commands.sh` for helper commands or use directly:

```bash
railway login              # Login to Railway
railway link               # Link to project
railway run <command>      # Run command in Railway environment
railway logs               # View logs
railway variables          # View/manage environment variables
railway up                 # Deploy manually
railway status             # Check service status
```

---

## 🎯 POST-DEPLOYMENT

### 1. Test All Features
- Login/logout
- Lead management
- Assignments
- Notes
- Notifications

### 2. Monitor Logs
- Check for errors
- Monitor performance
- Track usage

### 3. Set Up Alerts (Optional)
- Railway Pro plan includes alerts
- Set up monitoring for downtime
- Configure email notifications

---

## 📞 SUPPORT

**Railway Support:**
- Docs: https://docs.railway.app
- Discord: https://discord.gg/railway
- Email: support@railway.app

**Project Issues:**
- Check logs first
- Review this guide
- Check Railway status page

---

**Ready to deploy! Follow the steps above and your system will be live in ~20 minutes!** 🚀

