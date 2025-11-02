# 🔧 Railway Root Directory Configuration

## 🚨 The Problem

Railway is scanning your repository root, but your application code is in a subdirectory:

```
Repository Root: CURSOR---AI-Lead-Scoring-System-v1.0/
└── lead-scoring-system/
    ├── backend/          ← Your backend is here!
    └── frontend/         ← Your frontend is here!
```

**Railway Error:**
```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
The app contents that Railpack analyzed contains:
./
└── lead-scoring-system/
```

---

## ✅ The Solution

Set the **Root Directory** in Railway dashboard for each service.

---

## 📋 Step-by-Step Fix

### For Backend Service

1. **Go to Railway Dashboard**
   - Open https://railway.app
   - Select your project: `CURSOR---AI-Lead-Scoring-System-v1.0`

2. **Select Backend Service**
   - Click on the service (usually named after your repo or "web")

3. **Open Settings**
   - Click the **Settings** tab

4. **Set Root Directory**
   - Scroll down to **"Root Directory"** section
   - Enter: `lead-scoring-system/backend`
   - Click **Save** or press Enter

5. **Wait for Redeploy**
   - Railway will automatically trigger a new deployment
   - Watch the logs - it should now find `requirements.txt` and build correctly

---

### For Frontend Service

1. **Select Frontend Service**
   - If you have a separate frontend service, click on it
   - If not, create one: **+ New** → **GitHub Repo** → Select same repo

2. **Open Settings**
   - Click **Settings** tab

3. **Set Root Directory**
   - Set **Root Directory** to: `lead-scoring-system/frontend`
   - Click **Save**

4. **Wait for Redeploy**
   - Railway will rebuild with the correct path

---

## 🎯 Verification

After setting the root directory, Railway should:

1. **Find your files:**
   ```
   ✅ Found requirements.txt
   ✅ Found railway.json
   ✅ Found nixpacks.toml
   ```

2. **Build successfully:**
   ```
   ✅ Installing dependencies...
   ✅ Build complete
   ✅ Starting application...
   ```

3. **Start your app:**
   ```
   ✅ Uvicorn running on 0.0.0.0:$PORT
   ```

---

## 📸 Where to Find Root Directory Setting

In Railway Dashboard:
```
Service Name
├── Deployments
├── Variables
├── Metrics
└── Settings          ← Click here!
    ├── Service Name
    ├── Domain
    ├── Root Directory  ← Set to: lead-scoring-system/backend
    ├── Build Command
    └── Start Command
```

---

## 🔄 Alternative: Using Railway CLI

You can also set it via CLI:

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Set root directory (requires Railway CLI v2.0+)
railway variables set RAILWAY_ROOT_DIRECTORY=lead-scoring-system/backend
```

**Note:** This may not work for all Railway CLI versions. Using the dashboard is recommended.

---

## 🐛 Troubleshooting

### Still can't find files?

1. **Check the path:**
   - Make sure you typed exactly: `lead-scoring-system/backend`
   - No trailing slash
   - Case-sensitive (all lowercase)

2. **Verify files exist:**
   ```bash
   ls -la lead-scoring-system/backend/requirements.txt
   ls -la lead-scoring-system/backend/railway.json
   ```

3. **Check Railway logs:**
   - After setting root directory, check the deployment logs
   - You should see it looking in the correct path now

### Build still fails?

1. **Check build command:**
   - In Settings, verify **Build Command** is: `pip install -r requirements.txt`
   - Or leave it empty to use `railway.json` / `nixpacks.toml`

2. **Check start command:**
   - Verify **Start Command** is: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Or leave empty to use `railway.json`

### "Not found" errors?

- Make sure the root directory is relative to the repository root
- Do NOT include the repo name: ❌ `CURSOR---AI-Lead-Scoring-System-v1.0/lead-scoring-system/backend`
- Use the correct path: ✅ `lead-scoring-system/backend`

---

## 📚 Related Files

- `RAILWAY_QUICK_START.md` - Quick deployment guide (updated with root directory steps)
- `RAILWAY_DEPLOYMENT.md` - Complete deployment guide
- `railway-commands.sh` - CLI helper script

---

## ✅ Quick Checklist

- [ ] Backend service root directory set to: `lead-scoring-system/backend`
- [ ] Frontend service root directory set to: `lead-scoring-system/frontend`
- [ ] Both services saved and redeployed
- [ ] Build logs show files found correctly
- [ ] Applications are running

---

**After setting root directories, your deployments should work! 🚀**

