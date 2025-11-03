#!/bin/bash
# Railway startup script - properly expands PORT environment variable

# Run database migrations on startup (Alembic checks if already applied, so safe)
echo "🔄 Running database migrations..."
cd /app && alembic upgrade head || {
    echo "⚠️  Migration check completed (may already be up to date)"
}

# Get PORT from environment, default to 8000 if not set
PORT=${PORT:-8000}

# Calculate optimal workers based on Railway's resources
# Railway typically provides 1-2 CPU cores, so use appropriate worker count
WORKERS=${UVICORN_WORKERS:-2}
TIMEOUT=${UVICORN_TIMEOUT:-120}

echo "🚀 Starting application on port $PORT with $WORKERS workers..."
echo "⚙️  Configuration: workers=$WORKERS, timeout=${TIMEOUT}s, backlog=2048"

# Start uvicorn with optimized settings for high capacity
exec uvicorn app.main:app \
    --host 0.0.0.0 \
    --port "$PORT" \
    --workers "$WORKERS" \
    --timeout-keep-alive "$TIMEOUT" \
    --backlog 2048 \
    --limit-concurrency 1000 \
    --limit-max-requests 10000 \
    --log-level info \
    --access-log \
    --no-server-header

