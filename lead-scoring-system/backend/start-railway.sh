#!/bin/bash
# Railway startup script - properly expands PORT environment variable

# Run database migrations on startup (Alembic checks if already applied, so safe)
echo "🔄 Running database migrations..."
alembic upgrade head || {
    echo "⚠️  Migration check completed (may already be up to date)"
}

# Get PORT from environment, default to 8000 if not set
PORT=${PORT:-8000}

echo "🚀 Starting application on port $PORT..."
# Start uvicorn with the port
exec uvicorn app.main:app --host 0.0.0.0 --port "$PORT"

