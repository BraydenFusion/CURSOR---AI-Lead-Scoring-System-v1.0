#!/bin/bash
# Railway startup script - properly expands PORT environment variable

# Ensure we're in the correct directory
cd /app || cd "$(dirname "$0")/.." || exit 1

# Run database migrations using Python script (more reliable)
echo "🔄 Running database migrations..."

# Try Python migration script first
if [ -f "run_migrations.py" ]; then
    echo "📄 Using run_migrations.py..."
    if python3 run_migrations.py; then
        echo "✅ Migrations completed successfully via Python script"
    else
        echo "⚠️  Migration script failed, trying alembic directly..."
        # Fallback to direct alembic command
        if [ -f "alembic.ini" ]; then
            if alembic upgrade head; then
                echo "✅ Migrations completed successfully via alembic"
            else
                echo "❌ CRITICAL: Migrations failed - database tables may not exist!"
                echo "⚠️  Backend will start but login/registration will fail"
            fi
        else
            echo "❌ ERROR: alembic.ini not found!"
            echo "📁 Current directory: $(pwd)"
            ls -la
        fi
    fi
elif [ -f "alembic.ini" ]; then
    echo "⚠️  run_migrations.py not found, using alembic directly..."
    echo "📄 Found alembic.ini at $(pwd)/alembic.ini"
    CURRENT_REV=$(alembic current 2>/dev/null | grep -oP '\([^)]+\)' | head -1 | tr -d '()' || echo "")
    echo "📍 Current database revision: ${CURRENT_REV:-none}"
    
    if alembic upgrade head; then
        echo "✅ Migrations completed successfully"
    else
        echo "❌ Migration error - backend will continue but database features may not work"
        echo "⚠️  Check Railway deploy logs for detailed error messages"
    fi
else
    echo "❌ ERROR: Neither run_migrations.py nor alembic.ini found!"
    echo "📁 Current directory: $(pwd)"
    ls -la
    echo "⚠️  Skipping migrations - database schema may need manual setup"
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

