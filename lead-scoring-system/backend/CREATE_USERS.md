# 👥 Creating Test Users via API

## Quick Method (Recommended)

Once your backend server is running, use the provided script:

```bash
./create_users_via_api.sh
```

This will create all 4 test users automatically.

---

## Manual Method (Using curl)

If you prefer to create users manually, use these curl commands:

### 1. Admin User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@dealership.com",
    "username": "admin",
    "full_name": "Admin User",
    "password": "admin123",
    "role": "admin"
  }'
```

### 2. Manager User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "manager@dealership.com",
    "username": "manager",
    "full_name": "Sales Manager",
    "password": "manager123",
    "role": "manager"
  }'
```

### 3. Sales Rep 1
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rep1@dealership.com",
    "username": "rep1",
    "full_name": "Sales Rep 1",
    "password": "rep123",
    "role": "sales_rep"
  }'
```

### 4. Sales Rep 2
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "rep2@dealership.com",
    "username": "rep2",
    "full_name": "Sales Rep 2",
    "password": "rep123",
    "role": "sales_rep"
  }'
```

---

## Using API Documentation (Swagger UI)

1. Start your backend server: `cd backend && ./start.sh`
2. Open browser: http://localhost:8000/docs
3. Navigate to `/api/auth/register` endpoint
4. Click "Try it out"
5. Enter user data in the JSON body
6. Click "Execute"

Repeat for each user.

---

## Test User Credentials

Once created, use these to login:

| Role | Username | Password | Email |
|------|----------|----------|-------|
| Admin | `admin` | `admin123` | admin@dealership.com |
| Manager | `manager` | `manager123` | manager@dealership.com |
| Sales Rep 1 | `rep1` | `rep123` | rep1@dealership.com |
| Sales Rep 2 | `rep2` | `rep123` | rep2@dealership.com |

---

## Quick Start Complete Setup

```bash
# 1. Start infrastructure
cd lead-scoring-system
docker-compose up -d

# 2. Start backend (in new terminal)
cd backend
./start.sh

# 3. Create users (in another terminal)
cd backend
./create_users_via_api.sh

# 4. Start frontend (in another terminal)
cd frontend
./start.sh

# 5. Login at http://localhost:5173
```

---

## Troubleshooting

### "Server not responding"
- Make sure backend is running: `cd backend && ./start.sh`
- Check: http://localhost:8000/health should return `{"status": "healthy"}`

### "User already exists"
- That's okay! The user was already created previously.

### "Connection refused"
- Backend might not be started yet
- Check port 8000 is available
- Verify Docker containers are running: `docker-compose ps`

---

**Happy coding! 🚀**

