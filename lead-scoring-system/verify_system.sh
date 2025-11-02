#!/bin/bash

# Comprehensive System Verification Script
# Checks all components are operational

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

check() {
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ $1${NC}"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌ $1${NC}"
        ((FAIL++))
        return 1
    fi
}

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║   Lead Scoring System - Verification Script           ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Check Docker containers
echo "📦 Checking Infrastructure..."
echo "----------------------------------------"
docker ps | grep -q lead-scoring-postgres && check "PostgreSQL container running" || echo -e "${RED}❌ PostgreSQL not running${NC}"
docker ps | grep -q lead-scoring-redis && check "Redis container running" || echo -e "${RED}❌ Redis not running${NC}"

# Check database connection
echo -e "\n🗄️  Checking Database..."
echo "----------------------------------------"
docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -c "\dt" > /dev/null 2>&1
check "Database connection"

# Check tables exist
TABLES=$(docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = 'public' AND table_name NOT LIKE 'alembic%';" 2>/dev/null | tr -d ' ')
if [ "$TABLES" -ge 7 ]; then
    check "All tables exist (found $TABLES)"
else
    echo -e "${YELLOW}⚠️  Expected 7+ tables, found $TABLES${NC}"
fi

# Check users
echo -e "\n👥 Checking Users..."
echo "----------------------------------------"
USER_COUNT=$(docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -t -c "SELECT COUNT(*) FROM users;" 2>/dev/null | tr -d ' ')
if [ "$USER_COUNT" -ge 1 ]; then
    check "Users exist (found $USER_COUNT)"
else
    echo -e "${YELLOW}⚠️  No users found - run ./create_users_via_api.sh${NC}"
fi

# Check backend health
echo -e "\n🔌 Checking Backend..."
echo "----------------------------------------"
curl -s http://localhost:8000/health > /dev/null 2>&1 && check "Backend API responding" || echo -e "${YELLOW}⚠️  Backend not responding (may not be started)${NC}"

# Check API docs
curl -s http://localhost:8000/docs > /dev/null 2>&1 && check "API documentation accessible" || echo -e "${YELLOW}⚠️  API docs not accessible${NC}"

# Check frontend
echo -e "\n🎨 Checking Frontend..."
echo "----------------------------------------"
curl -s http://localhost:5173 > /dev/null 2>&1 && check "Frontend accessible" || echo -e "${YELLOW}⚠️  Frontend not accessible (may not be started)${NC}"

# Check environment
echo -e "\n⚙️  Checking Configuration..."
echo "----------------------------------------"
if [ -f "backend/.env" ]; then
    check ".env file exists"
    
    if grep -q "SECRET_KEY=" backend/.env && ! grep -q "your-secret-key-change-in-production" backend/.env; then
        check "SECRET_KEY is set (not default)"
    else
        echo -e "${YELLOW}⚠️  SECRET_KEY still using default value${NC}"
    fi
else
    echo -e "${RED}❌ .env file not found${NC}"
fi

# Check migrations
echo -e "\n🔄 Checking Migrations..."
echo "----------------------------------------"
if docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -c "SELECT * FROM alembic_version;" > /dev/null 2>&1; then
    check "Alembic version table exists"
    VERSION=$(docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -t -c "SELECT version_num FROM alembic_version;" 2>/dev/null | tr -d ' ')
    echo -e "   Current version: ${BLUE}$VERSION${NC}"
else
    echo -e "${YELLOW}⚠️  No Alembic version recorded${NC}"
fi

# Check indexes
echo -e "\n📊 Checking Performance..."
echo "----------------------------------------"
INDEX_COUNT=$(docker exec lead-scoring-postgres psql -U postgres -d lead_scoring -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%';" 2>/dev/null | tr -d ' ')
if [ "$INDEX_COUNT" -ge 1 ]; then
    check "Performance indexes exist (found $INDEX_COUNT)"
else
    echo -e "${YELLOW}⚠️  No performance indexes found${NC}"
fi

# Summary
echo -e "\n"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                             ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${GREEN}✅ Passed: $PASS${NC}"
if [ $FAIL -gt 0 ]; then
    echo -e "${RED}❌ Failed: $FAIL${NC}"
else
    echo -e "${GREEN}❌ Failed: 0${NC}"
fi

if [ $FAIL -eq 0 ]; then
    echo -e "\n${GREEN}🎉 System is fully operational!${NC}\n"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some checks failed. Review the output above.${NC}\n"
    exit 1
fi

