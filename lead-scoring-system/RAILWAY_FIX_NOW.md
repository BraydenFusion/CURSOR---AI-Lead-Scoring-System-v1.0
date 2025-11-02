# 🚨 URGENT: Railway Root Directory Fix

## The Error You're Seeing

```
⚠ Script start.sh not found
✖ Railpack could not determine how to build the app.
The app contents that Railpack analyzed contains:
./
└── lead-scoring-system/
```

## ⚡ Quick Fix (30 seconds)

### In Railway Dashboard:

1. **Click your service** (the one that failed)
2. **Click "Settings" tab**
3. **Find "Root Directory"** section
4. **Type:** `lead-scoring-system/backend`
5. **Click "Save"**
6. **Railway redeploys automatically** ✅

That's it! Railway will now look in the right place.

---

## 📍 Where to Find It

```
Railway Dashboard
└── Your Service
    ├── Deployments
    ├── Variables
    ├── Metrics
    └── Settings          ← Click here!
        └── Root Directory  ← Set to: lead-scoring-system/backend
```

---

## ✅ What Happens Next

After you save:
- Railway automatically starts a new deployment
- It will find `requirements.txt` in `lead-scoring-system/backend/`
- It will find `railway.json` and `nixpacks.toml`
- Build will succeed! 🎉

---

## 🔍 Verification

Check the new deployment logs. You should see:
```
✅ Installing dependencies from requirements.txt
✅ Build complete
✅ Starting uvicorn...
```

If you still see errors, double-check:
- ✅ Root Directory is exactly: `lead-scoring-system/backend`
- ✅ No trailing slash
- ✅ All lowercase

---

**That's all you need to do! Set the root directory and Railway will fix itself.** 🚀

For detailed troubleshooting, see: `RAILWAY_ROOT_DIRECTORY_FIX.md`

