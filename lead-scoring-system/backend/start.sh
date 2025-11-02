#!/bin/bash

# Lead Scoring System - Backend Startup Script

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Check for .env file
if [ ! -f ".env" ]; then
    echo_warn ".env file not found."
    if [ -f ".env.example" ]; then
        echo_info "Copying .env.example to .env..."
        cp .env.example .env
        echo_warn "Please update .env with your configuration before starting."
    else
        echo_warn "No .env.example found. Please create .env manually."
    fi
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo_info "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo_info "Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo_info "Checking dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check database connection
echo_info "Checking database connection..."
python -c "
from app.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('✓ Database connection successful')
except Exception as e:
    print(f'✗ Database connection failed: {e}')
    print('Make sure PostgreSQL is running and DATABASE_URL is correct in .env')
    exit(1)
" || exit 1

# Run migrations (optional - uncomment if you want auto-migration)
# echo_info "Checking database migrations..."
# alembic upgrade head || echo_warn "Migration check failed - run './migrate.sh upgrade' manually"

# Start the server
echo_info "Starting FastAPI server..."
echo_info "Server will be available at http://localhost:8000"
echo_info "API documentation at http://localhost:8000/docs"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

