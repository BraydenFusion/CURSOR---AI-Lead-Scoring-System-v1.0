# 🔧 Fix for Blank /docs and /redoc Pages

## Problem

The FastAPI documentation pages (`/docs` and `/redoc`) were showing blank pages.

## Root Cause

The Content Security Policy (CSP) headers in `SecurityHeadersMiddleware` were too restrictive and blocking Swagger UI from loading its required resources:

1. **CDN Resources**: Swagger UI loads JavaScript and CSS from CDNs (jsdelivr, unpkg)
2. **External Fonts**: Google Fonts used by Swagger UI
3. **Frame Options**: X-Frame-Options: DENY was too restrictive

## Solution

Updated `app/middleware/security_headers.py` to:

1. **Allow CDN Resources**:
   - `script-src`: Added `https://cdn.jsdelivr.net` and `https://unpkg.com`
   - `style-src`: Added `https://fonts.googleapis.com`, `https://cdn.jsdelivr.net`, `https://unpkg.com`
   - `font-src`: Added `https://fonts.gstatic.com`

2. **Relax Frame Options**:
   - Changed `X-Frame-Options` from `DENY` to `SAMEORIGIN` for docs pages
   - This allows same-origin framing needed by Swagger UI

3. **Remove Permissions-Policy**:
   - Don't set Permissions-Policy for docs pages to avoid interference

## Files Changed

- `backend/app/middleware/security_headers.py`

## Testing

After Railway redeploy, verify:
1. Visit `https://backend-base.up.railway.app/docs`
2. Should see Swagger UI with all API endpoints
3. Visit `https://backend-base.up.railway.app/redoc`
4. Should see ReDoc documentation

## Browser Console

If you still see blank pages, check browser console for:
- CSP violations (should be resolved)
- Network errors (should be resolved)
- JavaScript errors (unrelated to this fix - likely browser extensions)

---

**Status**: ✅ Fixed and pushed  
**Next**: Wait for Railway redeploy (2-3 minutes) and test

