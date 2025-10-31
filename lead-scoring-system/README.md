# Lead Scoring System (v1.0)

An AI-powered lead scoring and prioritization platform for car dealerships. Version 1.0 focuses on the core workflow: ingesting leads, tracking engagement activities, calculating scores, and presenting insights via a modern dashboard.

## Stack Overview
- Backend: FastAPI, SQLAlchemy, PostgreSQL, Redis, Pydantic
- Frontend: React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui, TanStack Query, Axios
- Tooling: Docker Compose, Alembic, Black, ESLint, Prettier

## Quick Start
1. Copy `.env.example` to `.env` and adjust values as needed.
2. Start infrastructure services:
   ```bash
   docker-compose up -d
   ```
3. Install backend dependencies and run the API:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn app.main:app --reload
   ```
4. Install frontend dependencies and launch the dashboard:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Project Structure
See the PRD for the detailed breakdown of backend and frontend modules. The repository follows the structure outlined in the project brief to keep modules decoupled and maintainable.

## Development Notes
- Use the provided Docker services for local PostgreSQL and Redis.
- Apply Alembic migrations before running the API.
- Seed data will be provided under `backend/app/seed.py` (to be implemented).
- Ensure code formatting with Black (Python) and Prettier (TypeScript).

## Next Steps
- Implement database models, schemas, and migrations.
- Build the scoring service and API routes.
- Develop the React dashboard with filtering, sorting, and score breakdown.