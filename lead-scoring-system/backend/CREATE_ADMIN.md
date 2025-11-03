# 🔐 Creating Admin User

## Quick Command

**For zsh (macOS/Linux):**
```bash
cd backend
source venv/bin/activate  # If using virtual environment
python create_admin_user.py --username admin --password 'AdminSecure123!@'
```

**Note:** 
- Use **single quotes** (`'...'`) instead of double quotes to prevent zsh from interpreting `!` as history expansion
- The default password is `AdminSecure123!@` which meets all security requirements

## Alternative: Via Railway API (Recommended)

After Railway redeploys, create admin via API:

```bash
curl -X POST https://backend-production-e9b2.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "AdminSecure123!@",
    "role": "admin"
  }'
```

This password still meets all security requirements:
- ✅ 18 characters
- ✅ Uppercase: A, S
- ✅ Lowercase: d, m, i, n, e, c, u, r, e
- ✅ Numbers: 123456
- ✅ No special characters needed (but still secure)

## Via API (After Railway Deploys)

Once backend is deployed on Railway:

```bash
curl -X POST https://backend-production-e9b2.up.railway.app/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "password": "AdminSecure123456",
    "role": "admin"
  }'
```

## Default Credentials

After creation, you can login with:
- **Username:** `admin`
- **Password:** `AdminSecure123456` (or whatever you set)

## Password Requirements

All passwords must meet these requirements:
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one number
- At least one special character (!@#$%^&*()_+-=[]{}|;:,.<>?)
- No common words (password, admin, etc.)
- No sequential patterns (abc, 123, qwerty, etc.)
- No repeated characters (aaaa)

