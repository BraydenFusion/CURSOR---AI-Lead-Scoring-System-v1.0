#!/bin/bash

# Lead Scoring System - Database Migration Helper
# This script helps manage database migrations

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo_warn ".env file not found. Creating from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo_info ".env file created. Please update it with your configuration."
    else
        echo_error ".env.example not found. Please create .env file manually."
        exit 1
    fi
fi

# Check if virtual environment is activated
if [ -z "$VIRTUAL_ENV" ] && [ -d "venv" ]; then
    echo_info "Activating virtual environment..."
    source venv/bin/activate
fi

# Function to check if database is accessible
check_database() {
    echo_info "Checking database connection..."
    python -c "
from app.database import engine
from sqlalchemy import text
try:
    with engine.connect() as conn:
        conn.execute(text('SELECT 1'))
    print('Database connection successful')
except Exception as e:
    print(f'Database connection failed: {e}')
    exit(1)
" || exit 1
}

# Main menu
case "$1" in
    "init")
        echo_info "Initializing database with Alembic..."
        check_database
        alembic revision --autogenerate -m "Initial migration"
        alembic upgrade head
        echo_info "Database initialized successfully!"
        ;;
    
    "create")
        if [ -z "$2" ]; then
            echo_error "Please provide a migration message: ./migrate.sh create 'your message'"
            exit 1
        fi
        echo_info "Creating new migration: $2"
        check_database
        alembic revision --autogenerate -m "$2"
        echo_info "Migration created. Review the file in alembic/versions/ and run './migrate.sh upgrade'"
        ;;
    
    "upgrade")
        echo_info "Upgrading database to latest migration..."
        check_database
        alembic upgrade head
        echo_info "Database upgraded successfully!"
        ;;
    
    "downgrade")
        if [ -z "$2" ]; then
            echo_warn "Downgrading one revision..."
            alembic downgrade -1
        else
            echo_info "Downgrading to revision: $2"
            alembic downgrade "$2"
        fi
        echo_info "Database downgraded!"
        ;;
    
    "status")
        echo_info "Current migration status:"
        alembic current
        echo_info ""
        echo_info "Available migrations:"
        alembic history
        ;;
    
    "stamp")
        if [ -z "$2" ]; then
            echo_error "Please provide a revision to stamp: ./migrate.sh stamp <revision>"
            exit 1
        fi
        echo_info "Stamping database to revision: $2"
        alembic stamp "$2"
        ;;
    
    "phase4")
        echo_info "Running Phase 4 migration (notes, notifications, lead status)..."
        check_database
        alembic revision --autogenerate -m "Add notes, notifications, and lead status"
        alembic upgrade head
        echo_info "Phase 4 migration completed!"
        ;;
    
    *)
        echo "Lead Scoring System - Migration Helper"
        echo ""
        echo "Usage: ./migrate.sh <command> [options]"
        echo ""
        echo "Commands:"
        echo "  init              - Initialize database (create initial migration and apply)"
        echo "  create <message>  - Create a new migration with autogenerate"
        echo "  upgrade           - Upgrade database to latest migration"
        echo "  downgrade [rev]   - Downgrade database (default: -1, or specify revision)"
        echo "  status            - Show current migration status and history"
        echo "  stamp <revision>  - Stamp database to a specific revision"
        echo "  phase4            - Quick command for Phase 4 migration"
        echo ""
        echo "Examples:"
        echo "  ./migrate.sh phase4              # Run Phase 4 migration"
        echo "  ./migrate.sh create 'Add field'  # Create new migration"
        echo "  ./migrate.sh upgrade             # Apply all pending migrations"
        exit 1
        ;;
esac

