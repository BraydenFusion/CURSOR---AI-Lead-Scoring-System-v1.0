# Your Sales Rep Account Credentials

## 🎯 Account Information

Once the backend redeploys with the enum fix, your account will be ready to use:

- **Username:** `brayden`
- **Password:** `Brayden@Secure2024!`
- **Email:** `bsaundersjones@gmail.com`
- **Full Name:** Brayden Saunders-Jones
- **Company Role:** VP Sales
- **System Role:** Sales Rep
- **Dashboard:** `/dashboard/sales-rep`

## 📝 How to Create Your Account

### Option 1: Wait for Backend Redeploy, Then Use Web Interface (Easiest)

1. Wait for Railway to redeploy the backend (usually 2-3 minutes after the latest push)
2. Go to: **https://ventrix.tech/register** or **https://frontend-production-e9b2.up.railway.app/register**
3. Fill in the registration form:
   - **Email:** bsaundersjones@gmail.com
   - **Username:** brayden
   - **Full Name:** Brayden Saunders-Jones
   - **Password:** Brayden@Secure2024!
   - **Company Role:** VP Sales
4. Click "Sign Up"
5. You'll be automatically logged in and redirected to your dashboard

### Option 2: Use the API (After Backend Redeploys)

Run this curl command:

```bash
curl -X POST "https://backend-base.up.railway.app/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "bsaundersjones@gmail.com",
    "username": "brayden",
    "full_name": "Brayden Saunders-Jones",
    "password": "Brayden@Secure2024!",
    "company_role": "VP Sales",
    "role": "sales_rep"
  }'
```

### Option 3: Use the Python Script (After Backend Redeploys)

```bash
cd backend
python3 create_my_account.py
```

## 🔐 Login After Account Creation

1. Go to: **https://ventrix.tech/login** or **https://frontend-production-e9b2.up.railway.app/login**
2. Enter your credentials:
   - **Username:** `brayden`
   - **Password:** `Brayden@Secure2024!`
3. Click "Sign In"
4. You'll be redirected to `/dashboard/sales-rep`

## ✅ Check Backend Status

Before creating your account, verify the backend is running:

```bash
curl https://backend-base.up.railway.app/health
```

You should see a JSON response with status information.

## 🔧 Troubleshooting

### If you get "enum error" when registering:
- The backend may not have redeployed yet
- Wait 2-3 minutes and try again
- Check Railway deploy logs to confirm the latest code is deployed

### If account already exists:
- Try logging in with the credentials above
- Or use a different username/email

### If password doesn't meet requirements:
- Must be at least 12 characters
- Must have uppercase, lowercase, number, and special character
- Cannot contain sequential characters (123, abc, etc.)
- The password `Brayden@Secure2024!` meets all requirements

## 📊 What You Can Do After Login

Once logged in as a Sales Rep, you can:
- View your assigned leads
- Track lead scores and classifications
- Add notes and activities to leads
- Monitor your sales pipeline
- Update lead status
- Access AI-powered insights

## 🔄 Next Steps

1. **Wait for backend redeploy** (check Railway dashboard)
2. **Create your account** using one of the methods above
3. **Log in** and explore your dashboard
4. **Change your password** after first login (Settings → Security)
5. **Start managing leads!**

---

**Note:** The enum fix has been pushed to GitHub. Railway will automatically redeploy the backend. Check the Railway dashboard to see when the deployment completes.

