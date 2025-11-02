#!/bin/bash

# Railway Deployment Helper Script

set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}🚂 Railway Deployment Commands${NC}"
echo "================================"
echo ""

case "$1" in
  setup)
    echo -e "${BLUE}Installing Railway CLI...${NC}"
    if command -v npm &> /dev/null; then
      npm install -g @railway/cli
      echo -e "${GREEN}✅ Railway CLI installed${NC}"
    else
      echo -e "${YELLOW}⚠️  npm not found. Install Node.js first.${NC}"
      exit 1
    fi
    echo ""
    echo "Next: Run './railway-commands.sh login'"
    ;;

  login)
    echo -e "${BLUE}Logging into Railway...${NC}"
    railway login
    echo -e "${GREEN}✅ Logged in${NC}"
    ;;

  link)
    echo -e "${BLUE}Linking to Railway project...${NC}"
    echo "Make sure you're in the project directory"
    railway link
    echo -e "${GREEN}✅ Linked to Railway project${NC}"
    ;;

  migrate)
    echo -e "${BLUE}Running database migrations...${NC}"
    cd backend
    railway run alembic upgrade head
    echo -e "${GREEN}✅ Migrations complete${NC}"
    ;;

  users)
    echo -e "${BLUE}Creating test users...${NC}"
    cd backend
    railway run python create_test_users.py
    echo -e "${GREEN}✅ Users created${NC}"
    ;;

  logs)
    echo -e "${BLUE}Viewing logs...${NC}"
    railway logs
    ;;

  vars)
    echo -e "${BLUE}Viewing environment variables...${NC}"
    railway variables
    ;;

  shell)
    echo -e "${BLUE}Opening shell in container...${NC}"
    railway run bash
    ;;

  deploy)
    echo -e "${BLUE}Deploying manually...${NC}"
    railway up
    ;;

  status)
    echo -e "${BLUE}Checking service status...${NC}"
    railway status
    ;;

  backend-shell)
    echo -e "${BLUE}Opening shell in backend container...${NC}"
    cd backend
    railway run bash
    ;;

  backend-logs)
    echo -e "${BLUE}Viewing backend logs...${NC}"
    cd backend
    railway logs
    ;;

  frontend-logs)
    echo -e "${BLUE}Viewing frontend logs...${NC}"
    cd frontend
    railway logs
    ;;

  *)
    echo "Usage: ./railway-commands.sh [command]"
    echo ""
    echo -e "${BLUE}Setup Commands:${NC}"
    echo "  setup         - Install Railway CLI"
    echo "  login         - Login to Railway"
    echo "  link          - Link to Railway project"
    echo ""
    echo -e "${BLUE}Database Commands:${NC}"
    echo "  migrate       - Run database migrations"
    echo "  users         - Create test users"
    echo ""
    echo -e "${BLUE}Management Commands:${NC}"
    echo "  logs          - View all service logs"
    echo "  backend-logs  - View backend logs only"
    echo "  frontend-logs - View frontend logs only"
    echo "  vars          - View environment variables"
    echo "  status        - Check service status"
    echo "  deploy        - Manually deploy"
    echo ""
    echo -e "${BLUE}Development Commands:${NC}"
    echo "  shell         - Open shell in default service"
    echo "  backend-shell - Open shell in backend container"
    echo ""
    echo -e "${YELLOW}Example workflow:${NC}"
    echo "  1. ./railway-commands.sh setup"
    echo "  2. ./railway-commands.sh login"
    echo "  3. cd backend && railway link"
    echo "  4. ./railway-commands.sh migrate"
    echo "  5. ./railway-commands.sh users"
    ;;
esac

