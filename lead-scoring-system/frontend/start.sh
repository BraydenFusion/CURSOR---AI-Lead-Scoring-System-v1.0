#!/bin/bash

# Lead Scoring System - Frontend Startup Script

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

# Check for node_modules
if [ ! -d "node_modules" ]; then
    echo_info "Installing dependencies..."
    npm install
fi

# Check for .env file (optional)
if [ ! -f ".env" ] && [ ! -f ".env.local" ]; then
    echo_warn "No .env file found. Using default API URL: http://localhost:8000/api"
    echo_warn "Create .env.local to customize: VITE_API_BASE_URL=your-api-url"
fi

# Start development server
echo_info "Starting development server..."
echo_info "Frontend will be available at http://localhost:5173"
echo ""

npm run dev

