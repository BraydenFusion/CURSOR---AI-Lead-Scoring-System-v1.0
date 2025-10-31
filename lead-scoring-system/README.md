# Lead Scoring System (MVP)

AI-powered lead scoring and prioritization system for car dealerships.

## Stack Overview

- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis
- Frontend: React (Vite + TypeScript), Tailwind CSS, shadcn/ui
- Tooling: Docker Compose, Alembic, TanStack Query

## Getting Started

1. Copy `.env.example` to `.env` and update credentials as needed.
2. Start services: `docker-compose up -d`
3. Backend: `cd backend && uvicorn app.main:app --reload`
4. Frontend: `cd frontend && npm install && npm run dev`

Further documentation will be added as the implementation progresses.
