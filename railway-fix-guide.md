# 🔧 Railway Root Directory Fix

## The Problem
Railway is looking at the repository root (`/`), but your backend is in `lead-scoring-system/backend/`.

Railway sees:
```
./
└── lead-scoring-system/
```

But needs to look in:
```
lead-scoring-system/backend/
```

## Solution: Set Root Directory in Railway Dashboard

### For Backend Service:
1. Go to Railway Dashboard
2. Select your **backend service**
3. Click **Settings** tab
4. Scroll to **"Root Directory"**
5. Set to: `lead-scoring-system/backend`
6. Click **Save**
7. Railway will redeploy automatically

### For Frontend Service:
1. Select your **frontend service**
2. Click **Settings** tab
3. Set **Root Directory** to: `lead-scoring-system/frontend`
4. Click **Save**

## Alternative: Monorepo Configuration

If you prefer automatic detection, we can add a root-level railway.json file.
