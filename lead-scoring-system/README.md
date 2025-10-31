# Lead Scoring System (MVP)

AI-powered lead scoring and prioritization system for car dealerships.

## Stack Overview

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis
- Frontend: React (Vite + TypeScript), Tailwind CSS, shadcn/ui
- Tooling: Docker Compose, Alembic, TanStack Query

## Getting Started

1. Copy `.env.example` to `.env` and update credentials as needed.
2. Start infrastructure:
   ```bash
   docker compose up -d
   ```
3. Install backend dependencies and run migrations:
   ```bash
   cd backend
   pip install -r requirements.txt
   python3 -m alembic upgrade head
   ```
4. (Optional) Seed the database with sample leads:
   ```bash
   python3 seed_data.py
   ```
5. Launch the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
6. In a new terminal, set up and start the frontend:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

With all services running you can visit http://localhost:5173 to explore the dashboard and http://localhost:8000/docs for interactive API docs.

## Key Features (v1.0)

- PostgreSQL schema managed via Alembic migrations
- FastAPI endpoints for leads, activities, and score breakdowns
- Deterministic AI scoring service with category breakdowns & history tracking
- Seed script populating Hot/Warm/Cold exemplar leads
- React + Vite dashboard with shadcn/ui components, filters, and modal breakdowns
