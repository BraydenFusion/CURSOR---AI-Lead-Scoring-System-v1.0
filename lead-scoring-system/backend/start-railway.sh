#!/bin/bash
# Railway startup script - properly expands PORT environment variable

# Ensure we're in the correct directory
cd /app || cd "$(dirname "$0")/.." || exit 1

# Verify alembic.ini exists
if [ ! -f "alembic.ini" ]; then
    echo "⚠️  WARNING: alembic.ini not found in $(pwd)"
    echo "📁 Current directory contents:"
    ls -la
    echo "⚠️  Skipping migrations - database schema may need manual setup"
else
    # Run database migrations on startup
    echo "🔄 Running database migrations from $(pwd)..."
    echo "📄 Found alembic.ini at $(pwd)/alembic.ini"
    
    # Check current revision
    CURRENT_REV=$(alembic current 2>/dev/null | grep -oP '\([^)]+\)' | head -1 | tr -d '()' || echo "")
    echo "📍 Current database revision: ${CURRENT_REV:-none}"
    
    # Run migrations - if tables don't exist, initial migration will create them
    if alembic upgrade head; then
        echo "✅ Migrations completed successfully"
    else
        echo "⚠️  Migration error occurred - checking if tables exist..."
        # Check if this is a "table doesn't exist" error that we can recover from
        # If initial migration failed, try to stamp to 000 and retry
        if [ -z "$CURRENT_REV" ]; then
            echo "🔄 Database not initialized - stamping to 000_initial and retrying..."
            alembic stamp 000_initial 2>/dev/null || true
            alembic upgrade head || {
                echo "⚠️  Migration failed after retry - backend will continue but database features may not work"
            }
        else
            echo "⚠️  Migration error - backend will continue but some features may not work"
        fi
    fi
fi

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

