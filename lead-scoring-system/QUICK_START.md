# 🚀 Quick Start Guide

Get the Lead Scoring System up and running in 5 minutes!

---

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or use Docker)
- Docker & Docker Compose (optional)

---

## Option 1: Quick Start (Recommended)

### 1. Start Infrastructure

```bash
cd lead-scoring-system
docker-compose up -d
```

This starts PostgreSQL and Redis.

### 2. Backend Setup

```bash
cd backend

# Use helper script
./start.sh

# Or manually:
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env if needed
./migrate.sh phase4  # Run Phase 4 migrations
python create_test_users.py
uvicorn app.main:app --reload
```

Backend will run at: http://localhost:8000  
API docs at: http://localhost:8000/docs

### 3. Frontend Setup

```bash
cd frontend

# Use helper script
./start.sh

# Or manually:
npm install
npm run dev
```

Frontend will run at: http://localhost:5173

### 4. Login

- Admin: `username=admin`, `password=admin123`
- Manager: `username=manager`, `password=manager123`
- Sales Rep: `username=rep1`, `password=rep123`

---

## Option 2: Manual Setup

### Backend

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Update DATABASE_URL if needed

# Database setup
./migrate.sh phase4

# Create users
python create_test_users.py

# Start server
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Quick Commands

### Backend

```bash
# Migration
./migrate.sh phase4              # Run Phase 4 migration
./migrate.sh upgrade            # Apply all migrations
./migrate.sh status             # Check migration status

# Testing
pytest                          # Run all tests
pytest tests/test_auth.py      # Run specific test file

# Development
./start.sh                      # Start with checks
```

### Frontend

```bash
./start.sh                      # Start dev server
npm run build                   # Build for production
npm run preview                 # Preview production build
```

---

## Verify Installation

1. **Backend Health**: http://localhost:8000/health
2. **API Docs**: http://localhost:8000/docs
3. **Frontend**: http://localhost:5173
4. **Login**: Use test credentials above

---

## Common Issues

### Database Connection Error
- Check PostgreSQL is running: `docker ps` or `sudo systemctl status postgresql`
- Verify DATABASE_URL in `.env`

### Port Already in Use
- Backend: Change port in `uvicorn` command or kill existing process
- Frontend: Vite will prompt to use different port

### Migration Errors
- Ensure database exists: `createdb leadscoring` (or via Docker)
- Check database user permissions
- Run `./migrate.sh status` to see current state

### Module Not Found
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`

---

## Next Steps

1. ✅ System is running!
2. 📖 Read [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup
3. 🧪 Run tests: `cd backend && pytest`
4. 🔧 Customize configuration in `.env`

---

## Getting Help

- Check logs: `sudo journalctl -u leadscoring` (if using systemd)
- Review [LAUNCH_CHECKLIST.md](./LAUNCH_CHECKLIST.md)
- Check API documentation at `/docs` endpoint

---

**Happy Coding! 🎉**

