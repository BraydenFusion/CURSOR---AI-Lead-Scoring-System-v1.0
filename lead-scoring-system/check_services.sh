#!/bin/bash

# Service Status Checker
# Checks if all required services are running and listening

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}"
echo "╔════════════════════════════════════════════════════════╗"
echo "║       Service Status Checker                          ║"
echo "╚════════════════════════════════════════════════════════╝"
echo -e "${NC}\n"

# Service definitions
SERVICES=(
    "PostgreSQL:5433:lead-scoring-postgres"
    "Redis:6379:lead-scoring-redis"
    "Backend API:8000:backend"
    "Frontend:5173:frontend"
)

check_port() {
    local name=$1
    local port=$2
    local docker_container=$3
    
    echo -n "Checking $name (port $port)... "
    
    # Check if it's a Docker service
    if [ -n "$docker_container" ]; then
        if docker ps --format "{{.Names}}" | grep -q "^${docker_container}$"; then
            # Check if port is listening
            if nc -z localhost $port 2>/dev/null || lsof -i :$port > /dev/null 2>&1; then
                echo -e "${GREEN}✅ RUNNING${NC}"
                return 0
            else
                echo -e "${YELLOW}⚠️  Container running but port $port not accessible${NC}"
                return 1
            fi
        else
            echo -e "${RED}❌ NOT RUNNING${NC}"
            return 1
        fi
    else
        # Check non-Docker service
        if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1 || \
           curl -s -f "http://localhost:$port" > /dev/null 2>&1 || \
           nc -z localhost $port 2>/dev/null; then
            echo -e "${GREEN}✅ RUNNING${NC}"
            return 0
        else
            echo -e "${RED}❌ NOT RUNNING${NC}"
            return 1
        fi
    fi
}

check_docker_health() {
    local container=$1
    if docker ps --format "{{.Names}} {{.Status}}" | grep "$container" | grep -q "healthy\|Up"; then
        return 0
    fi
    return 1
}

# Check PostgreSQL
echo "📦 Infrastructure Services"
echo "----------------------------------------"
check_port "PostgreSQL" "5433" "lead-scoring-postgres"
if check_docker_health "lead-scoring-postgres"; then
    echo "   Status: $(docker ps --format '{{.Status}}' --filter 'name=lead-scoring-postgres')"
fi

check_port "Redis" "6379" "lead-scoring-redis"
if check_docker_health "lead-scoring-redis"; then
    echo "   Status: $(docker ps --format '{{.Status}}' --filter 'name=lead-scoring-redis')"
fi

# Check Backend
echo -e "\n🔌 Application Services"
echo "----------------------------------------"
check_port "Backend API" "8000" ""

# Check specific backend endpoints
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    HEALTH=$(curl -s http://localhost:8000/health | grep -o '"status":"[^"]*"' | cut -d'"' -f4)
    echo "   Health: ${GREEN}$HEALTH${NC}"
    echo "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
else
    echo "   Health: ${RED}Not accessible${NC}"
fi

# Check Frontend
check_port "Frontend" "5173" ""

if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   URL: ${BLUE}http://localhost:5173${NC}"
else
    echo "   URL: ${RED}Not accessible${NC}"
fi

# Summary
echo -e "\n"
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    SUMMARY                            ║"
echo "╚════════════════════════════════════════════════════════╝"

# Count running services
RUNNING=0
TOTAL=4

docker ps --format "{{.Names}}" | grep -q "lead-scoring-postgres" && ((RUNNING++))
docker ps --format "{{.Names}}" | grep -q "lead-scoring-redis" && ((RUNNING++))
curl -s http://localhost:8000/health > /dev/null 2>&1 && ((RUNNING++))
curl -s http://localhost:5173 > /dev/null 2>&1 && ((RUNNING++))

echo -e "${GREEN}✅ Running: $RUNNING/$TOTAL services${NC}"

if [ $RUNNING -eq $TOTAL ]; then
    echo -e "\n${GREEN}🎉 All services are running!${NC}"
    echo -e "\n📱 Access your system:"
    echo "   Frontend: ${BLUE}http://localhost:5173${NC}"
    echo "   API Docs: ${BLUE}http://localhost:8000/docs${NC}"
    exit 0
else
    echo -e "\n${YELLOW}⚠️  Some services are not running${NC}"
    echo -e "\n🔧 To start services:"
    echo "   1. Infrastructure: ${BLUE}docker-compose up -d${NC}"
    echo "   2. Backend: ${BLUE}cd backend && ./start.sh${NC}"
    echo "   3. Frontend: ${BLUE}cd frontend && ./start.sh${NC}"
    exit 1
fi

