# Create Your Sales Rep Account

## Quick Setup

Your account credentials have been pre-configured. Here's how to create your account:

### Option 1: Use the Registration API (Recommended)

Run this curl command to create your account:

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

### Option 2: Use the Python Script

If you have `requests` installed, run:

```bash
cd backend
python3 create_my_account.py
```

### Option 3: Register via the Web Interface

1. Go to: https://ventrix.tech/register (or https://frontend-production-e9b2.up.railway.app/register)
2. Fill in the registration form with:
   - **Email:** bsaundersjones@gmail.com
   - **Username:** brayden
   - **Full Name:** Brayden Saunders-Jones
   - **Password:** Brayden@Secure2024!
   - **Company Role:** VP Sales

## Your Login Credentials

After account creation, use these credentials to log in:

- **Username:** `brayden`
- **Password:** `Brayden@Secure2024!`
- **Email:** `bsaundersjones@gmail.com`
- **Role:** Sales Rep
- **Dashboard:** `/dashboard/sales-rep`

## Login URLs

- **Ventrix.tech:** https://ventrix.tech/login
- **Railway:** https://frontend-production-e9b2.up.railway.app/login

## Security Reminder

⚠️ **IMPORTANT:** 
- Change your password after first login
- Use a strong, unique password
- Never share your credentials
- Enable 2FA if available

## After Login

Once logged in, you'll be automatically redirected to your Sales Rep dashboard at `/dashboard/sales-rep` where you can:
- View and manage your assigned leads
- Track lead scores
- Add notes and activities
- Monitor your sales pipeline

## Troubleshooting

If you get an "already exists" error:
- The account may already be created
- Try logging in with the credentials above
- If you forgot your password, use the password reset feature

If you encounter any issues:
1. Check that the backend is running: https://backend-base.up.railway.app/health
2. Verify the frontend is accessible
3. Check Railway deploy logs for any errors

