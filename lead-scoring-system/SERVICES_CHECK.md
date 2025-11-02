# 🔍 Services to Check - Listening Ports

This guide shows you exactly which services should be listening and how to check them.

---

## 📋 Required Services

Your system needs **4 main services** running:

| Service | Port | Purpose | How to Start |
|---------|------|---------|--------------|
| **PostgreSQL** | 5433 | Database | `docker-compose up -d` |
| **Redis** | 6379 | Cache/Sessions | `docker-compose up -d` |
| **Backend API** | 8000 | FastAPI server | `cd backend && ./start.sh` |
| **Frontend** | 5173 | React app | `cd frontend && ./start.sh` |

---

## 🔍 Quick Check Commands

### Option 1: Use the Automated Script
```bash
cd lead-scoring-system
./check_services.sh
```

This will check all services automatically!

---

### Option 2: Manual Checks

#### Check PostgreSQL (Port 5433)
```bash
# Method 1: Check Docker container
docker ps | grep lead-scoring-postgres

# Method 2: Check if port is listening
nc -z localhost 5433 && echo "✅ PostgreSQL listening" || echo "❌ Not listening"

# Method 3: Test connection
docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -c "SELECT 1;"
```

**Expected:** Container running and port 5433 accessible

---

#### Check Redis (Port 6379)
```bash
# Method 1: Check Docker container
docker ps | grep lead-scoring-redis

# Method 2: Check if port is listening
nc -z localhost 6379 && echo "✅ Redis listening" || echo "❌ Not listening"

# Method 3: Test connection
docker exec lead-scoring-redis redis-cli ping
```

**Expected:** Should return `PONG`

---

#### Check Backend API (Port 8000)
```bash
# Method 1: Check if port is listening
nc -z localhost 8000 && echo "✅ Backend listening" || echo "❌ Not listening"

# Method 2: Test health endpoint
curl http://localhost:8000/health

# Method 3: Check process
lsof -i :8000
```

**Expected:** Returns `{"status": "healthy"}`

**What to check:**
- ✅ Health endpoint: `http://localhost:8000/health`
- ✅ API docs: `http://localhost:8000/docs`
- ✅ Root: `http://localhost:8000`

---

#### Check Frontend (Port 5173)
```bash
# Method 1: Check if port is listening
nc -z localhost 5173 && echo "✅ Frontend listening" || echo "❌ Not listening"

# Method 2: Test if accessible
curl -I http://localhost:5173

# Method 3: Check process
lsof -i :5173
```

**Expected:** Returns HTTP 200 status

**What to check:**
- ✅ Frontend: `http://localhost:5173`
- ✅ Should show login page in browser

---

## 🛠️ Complete Status Check (One Command)

```bash
echo "PostgreSQL:" && nc -z localhost 5433 && echo "✅" || echo "❌"
echo "Redis:" && nc -z localhost 6379 && echo "✅" || echo "❌"
echo "Backend:" && curl -s http://localhost:8000/health > /dev/null && echo "✅" || echo "❌"
echo "Frontend:" && curl -s http://localhost:5173 > /dev/null && echo "✅" || echo "❌"
```

---

## 📊 Detailed Service Information

### PostgreSQL (Database)
- **Port:** 5433 (mapped from container port 5432)
- **Container:** `lead-scoring-postgres`
- **Check:** `docker ps | grep postgres`
- **Test:** `docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -c "\dt"`
- **URL:** `postgresql://postgres:postgres@localhost:5433/lead_scoring`

### Redis (Cache)
- **Port:** 6379
- **Container:** `lead-scoring-redis`
- **Check:** `docker ps | grep redis`
- **Test:** `docker exec lead-scoring-redis redis-cli ping`
- **URL:** `redis://localhost:6379/0`

### Backend API (FastAPI)
- **Port:** 8000
- **Process:** Python (uvicorn)
- **Check:** `curl http://localhost:8000/health`
- **Endpoints:**
  - Health: `http://localhost:8000/health`
  - Docs: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`
  - API: `http://localhost:8000/api/*`

### Frontend (React/Vite)
- **Port:** 5173
- **Process:** Node.js (vite)
- **Check:** `curl http://localhost:5173`
- **URL:** `http://localhost:5173`

---

## 🔧 Troubleshooting

### Service Not Listening? Check These:

#### PostgreSQL Not Running
```bash
# Start it
docker-compose up -d postgres

# Check logs
docker logs lead-scoring-postgres

# Verify port
docker port lead-scoring-postgres
```

#### Redis Not Running
```bash
# Start it
docker-compose up -d redis

# Check logs
docker logs lead-scoring-redis

# Test connection
docker exec lead-scoring-redis redis-cli ping
```

#### Backend Not Running
```bash
# Check if process is running
ps aux | grep uvicorn

# Check if port is in use
lsof -i :8000

# Start backend
cd backend
./start.sh

# Check logs
tail -f logs/app.log
```

#### Frontend Not Running
```bash
# Check if process is running
ps aux | grep vite

# Check if port is in use
lsof -i :5173

# Start frontend
cd frontend
./start.sh

# Check for errors in terminal
```

---

## 🎯 Port Conflicts

If a port is already in use:

### Check What's Using Port 8000
```bash
lsof -i :8000
# Or
sudo netstat -tulpn | grep :8000
```

### Check What's Using Port 5173
```bash
lsof -i :5173
# Or
sudo netstat -tulpn | grep :5173
```

### Kill Process on Port (if needed)
```bash
# Find PID
lsof -ti :8000

# Kill it (replace PID)
kill -9 <PID>
```

---

## 🔍 Advanced Checking

### Check All Listening Ports
```bash
# See all listening ports
netstat -an | grep LISTEN | grep -E "5433|6379|8000|5173"

# Or using lsof
lsof -i -P -n | grep -E "5433|6379|8000|5173"

# Or using ss (modern alternative)
ss -tulpn | grep -E "5433|6379|8000|5173"
```

### Check Docker Containers
```bash
# All containers
docker ps -a

# Just running
docker ps

# Specific service
docker ps | grep lead-scoring
```

### Check Service Health
```bash
# PostgreSQL
docker exec lead-scoring-postgres pg_isready -U postgres

# Redis
docker exec lead-scoring-redis redis-cli ping

# Backend
curl http://localhost:8000/health

# Frontend
curl -I http://localhost:5173
```

---

## 📱 Network Access

### From Same Machine
- Use: `http://localhost:8000` or `http://127.0.0.1:8000`

### From Other Devices on Network
1. Find your IP:
   ```bash
   # Mac/Linux
   ifconfig | grep "inet " | grep -v 127.0.0.1
   
   # Or
   hostname -I
   ```

2. Use your IP:
   - Backend: `http://<your-ip>:8000`
   - Frontend: `http://<your-ip>:5173`

**Note:** Make sure firewall allows connections!

---

## ✅ Quick Status Check

Run this to see everything at once:

```bash
./check_services.sh
```

Or manually:

```bash
echo "=== SERVICE STATUS ==="
echo "PostgreSQL (5433):" $(nc -z localhost 5433 2>/dev/null && echo "✅" || echo "❌")
echo "Redis (6379):" $(nc -z localhost 6379 2>/dev/null && echo "✅" || echo "❌")
echo "Backend (8000):" $(curl -s http://localhost:8000/health > /dev/null && echo "✅" || echo "❌")
echo "Frontend (5173):" $(curl -s http://localhost:5173 > /dev/null && echo "✅" || echo "❌")
```

---

## 🎯 Summary

**Services to Check:**
1. ✅ **PostgreSQL** on port **5433**
2. ✅ **Redis** on port **6379**
3. ✅ **Backend API** on port **8000**
4. ✅ **Frontend** on port **5173**

**Quick Check:**
```bash
./check_services.sh
```

**Access URLs:**
- Frontend: http://localhost:5173
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

