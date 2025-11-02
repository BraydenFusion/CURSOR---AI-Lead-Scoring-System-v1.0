# 🌐 Visual Access Guide

How to access your Lead Scoring System visually in your web browser.

---

## 🚀 Quick Start (All Services)

### Step 1: Start Infrastructure
```bash
cd lead-scoring-system
docker-compose up -d
```

Wait ~10 seconds for containers to start.

---

### Step 2: Start Backend

**Terminal 1:**
```bash
cd backend
./start.sh
```

Wait for: `Application startup complete`

**You'll see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

---

### Step 3: Create Test Users

**Terminal 2 (after backend starts):**
```bash
cd backend
./create_users_via_api.sh
```

---

### Step 4: Start Frontend

**Terminal 3:**
```bash
cd frontend
./start.sh
```

Wait for: `Local: http://localhost:5173/`

---

## 🌐 Access URLs

Once all services are running, open these in your web browser:

### 1. 🎨 **Frontend Application (Main UI)**
```
http://localhost:5173
```
**What you'll see:**
- Login page
- After login: Dashboard with leads
- Navigation menu
- All application features

**Login Credentials:**
- Admin: `admin` / `admin123`
- Manager: `manager` / `manager123`
- Sales Rep: `rep1` / `rep123`

---

### 2. 📚 **API Documentation (Swagger UI)**
```
http://localhost:8000/docs
```
**What you'll see:**
- Interactive API documentation
- All available endpoints
- "Try it out" feature to test APIs
- Request/response schemas
- Authentication options

**Features:**
- Click "Try it out" on any endpoint
- Enter parameters
- Execute requests
- See live responses

---

### 3. 📖 **Alternative API Docs (ReDoc)**
```
http://localhost:8000/redoc
```
**What you'll see:**
- Alternative API documentation format
- Clean, readable interface
- Complete API reference

---

### 4. ❤️ **Backend Health Check**
```
http://localhost:8000/health
```
**What you'll see:**
```json
{"status": "healthy"}
```

---

### 5. 🏠 **Backend Root**
```
http://localhost:8000
```
**What you'll see:**
```json
{
  "message": "Lead Scoring System v2.0",
  "status": "operational"
}
```

---

## 🎯 Visual Access Summary

| Service | URL | Purpose |
|---------|-----|---------|
| **Frontend** | http://localhost:5173 | Main application UI |
| **API Docs (Swagger)** | http://localhost:8000/docs | Interactive API documentation |
| **API Docs (ReDoc)** | http://localhost:8000/redoc | Alternative API docs |
| **Health Check** | http://localhost:8000/health | Backend status |
| **API Root** | http://localhost:8000 | Backend welcome |

---

## 🖥️ What Each Interface Looks Like

### Frontend (http://localhost:5173)

**Login Page:**
- Clean login form
- Username and password fields
- "Sign In" button
- "Forgot password?" link

**Dashboard (After Login):**
- Lead cards in grid layout
- Filter dropdowns (Classification, Sort)
- Score badges (HOT/WARM/COLD)
- Notification bell in header
- User info in navigation

**Features:**
- Click lead card → Score breakdown modal
- "My Leads" button (for sales reps)
- Notification dropdown
- Logout button

---

### API Documentation (http://localhost:8000/docs)

**Swagger UI:**
- Left sidebar: All API endpoints grouped by tags
- Main area: Endpoint details
- "Try it out" buttons to test APIs
- Request/response examples
- Authentication: "Authorize" button at top

**How to Use:**
1. Click "Authorize" button
2. Enter: `Bearer <your-token>` or use the login endpoint first
3. Click any endpoint → "Try it out"
4. Fill in parameters
5. Click "Execute"
6. See response below

**Example - Test Login:**
1. Find `/api/auth/login`
2. Click "Try it out"
3. Enter username and password
4. Execute
5. Copy the `access_token` from response
6. Use it in "Authorize" button

---

### Backend Health (http://localhost:8000/health)

Simple JSON response:
```json
{
  "status": "healthy"
}
```

---

## 🔍 Troubleshooting Access

### "Cannot access http://localhost:5173"

**Check:**
```bash
# Is frontend running?
cd frontend
npm run dev

# Check for errors in terminal
```

**Solution:**
- Make sure frontend is started
- Check terminal for any errors
- Try different browser
- Clear browser cache

---

### "Cannot access http://localhost:8000/docs"

**Check:**
```bash
# Is backend running?
curl http://localhost:8000/health

# If fails, start backend:
cd backend
./start.sh
```

**Solution:**
- Backend must be running first
- Wait for "Application startup complete"
- Check for port conflicts (another app on 8000?)

---

### "Connection refused" or "ERR_CONNECTION_REFUSED"

**Causes:**
1. Service not started
2. Wrong port
3. Firewall blocking

**Solution:**
```bash
# Check what's running on ports
lsof -i :8000  # Backend
lsof -i :5173  # Frontend

# Restart services
docker-compose restart
cd backend && ./start.sh
cd frontend && ./start.sh
```

---

### "404 Not Found" on Frontend Routes

**Cause:** React Router needs all routes to serve index.html

**Check:**
- Are you accessing `/dashboard` or other routes directly?
- Should work if navigating from login

**Solution:**
- Always start from http://localhost:5173 (root)
- Use navigation within the app

---

## 🎬 Quick Demo Sequence

1. **Open API Docs** → http://localhost:8000/docs
   - See all available endpoints
   - Try the login endpoint

2. **Open Frontend** → http://localhost:5173
   - See login page
   - Login with test credentials
   - Explore dashboard

3. **Test Features:**
   - Click a lead card → See score breakdown
   - Check notifications
   - Navigate to "My Leads" (if sales rep)
   - Add a note to a lead

---

## 📱 Mobile Access

**Access from mobile device on same network:**

1. Find your computer's IP address:
   ```bash
   # Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Or
   ipconfig getifaddr en0
   ```

2. Use your computer's IP:
   - Frontend: `http://<your-ip>:5173`
   - Backend: `http://<your-ip>:8000`

3. Make sure firewall allows connections

**Note:** For production, use proper domain names and HTTPS.

---

## 🔒 Security Note

**Development (Current Setup):**
- ✅ CORS allows `localhost` and `*`
- ✅ Accessible on local network
- ✅ No HTTPS required

**Production:**
- ⚠️ Restrict CORS to your domain only
- ⚠️ Enable HTTPS/SSL
- ⚠️ Use firewall rules
- ⚠️ Don't expose to public internet without security

---

## 🎯 Quick Reference

**Start Everything:**
```bash
# Terminal 1
docker-compose up -d

# Terminal 2
cd backend && ./start.sh

# Terminal 3 (after backend starts)
cd backend && ./create_users_via_api.sh

# Terminal 4
cd frontend && ./start.sh
```

**Then Open:**
1. Frontend: http://localhost:5173
2. API Docs: http://localhost:8000/docs
3. Health: http://localhost:8000/health

---

## 📸 What to Expect

### Frontend Login Page
- Centered card with "Lead Scoring System" title
- Username and password fields
- "Sign In" button
- Clean, modern design

### Dashboard
- Grid of lead cards (3 test leads)
- Each card shows:
  - Name
  - Score (big number)
  - Classification badge (HOT/WARM/COLD)
  - Email
  - Source
- Filter and sort controls at top
- Navigation bar with user info

### API Documentation
- Professional Swagger interface
- Organized by endpoint groups
- Interactive testing capability
- Code examples
- Authentication section

---

**Happy exploring! 🚀**

