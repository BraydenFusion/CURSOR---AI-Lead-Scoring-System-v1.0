#!/bin/bash
# Railway Database Setup Script
# Run this after: railway login && railway link

set -e

echo "🚀 Railway Database Setup"
echo "========================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Check if logged in
if ! railway whoami &> /dev/null; then
    echo "⚠️  Not logged in. Please run: railway login"
    exit 1
fi

# Check if linked to project
if ! railway status &> /dev/null; then
    echo "⚠️  Not linked to project. Please run: railway link"
    exit 1
fi

echo "✅ Railway CLI installed and authenticated"
echo ""

# Navigate to backend
cd backend

echo "📦 Running database migrations..."
railway run alembic upgrade head

echo ""
echo "✅ Migrations complete!"
echo ""

echo "🔍 Verifying tables were created..."
railway run python -c "from app.database import engine; from sqlalchemy import inspect; inspector = inspect(engine); tables = inspector.get_table_names(); print('Tables:', tables); print('✅ Total tables:', len(tables))"

echo ""
echo "✅ Database setup complete!"
echo ""
echo "Next steps:"
echo "  1. Create test users: railway run python create_test_users.py"
echo "  2. Or create users via API (see RAILWAY_API_TESTING.md)"

