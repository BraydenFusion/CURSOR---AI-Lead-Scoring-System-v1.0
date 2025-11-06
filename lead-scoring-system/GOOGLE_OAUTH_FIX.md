# Fix Google OAuth redirect_uri_mismatch Error

## Problem
Firebase Authentication uses its own redirect handler: `https://ventrix-477422.firebaseapp.com/_/auth/handler`

This redirect URI must be added to your Google OAuth 2.0 client configuration in Google Cloud Console.

## Solution: Add Redirect URI to Google Cloud Console

### Step 1: Find Your OAuth 2.0 Client ID
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Select your project: **ventrix-477422** (or the project associated with your Firebase project)
3. Navigate to **APIs & Services** → **Credentials**
4. Find your **OAuth 2.0 Client ID** (it should be associated with your Firebase project)

### Step 2: Add Authorized Redirect URIs
1. Click on your OAuth 2.0 Client ID to edit it
2. Under **Authorized redirect URIs**, click **+ ADD URI**
3. Add these redirect URIs:
   - `https://ventrix-477422.firebaseapp.com/__/auth/handler`
   - `https://ventrix-477422.web.app/__/auth/handler`
   - `https://frontend-production-e9b2.up.railway.app/__/auth/handler` (your Railway frontend domain)
   - `https://frontend-production-e9b2.up.railway.app` (your Railway frontend domain root)

4. Click **SAVE**

### Step 3: Verify Firebase Authorized Domains
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select your project: **VENTRIX**
3. Navigate to **Authentication** → **Settings** → **Authorized domains**
4. Ensure these domains are listed:
   - `ventrix-477422.firebaseapp.com` (Default)
   - `ventrix-477422.web.app` (Default)
   - `frontend-production-e9b2.up.railway.app` (Custom) ✅ Already added

### Step 4: Test
After adding the redirect URIs, try Google Sign-In again. The error should be resolved.

## Alternative: Direct Google OAuth (Without Firebase)

If you continue to have issues with Firebase's redirect handler, we can implement Google OAuth directly without Firebase. This gives you more control over the redirect flow.

Let me know if you'd like me to implement this alternative approach.

