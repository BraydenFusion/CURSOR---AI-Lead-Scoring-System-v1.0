#!/bin/bash

# Script to create test users via API
# Make sure the backend server is running first!
# Usage: ./create_users_via_api.sh

API_URL="http://localhost:8000/api/auth/register"

echo "🔐 Creating Test Users via API..."
echo "=================================="
echo ""
echo "⚠️  Make sure the backend server is running at http://localhost:8000"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

create_user() {
    local email=$1
    local username=$2
    local full_name=$3
    local password=$4
    local role=$5
    
    echo -n "Creating ${full_name}... "
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$API_URL" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$email\",
            \"username\": \"$username\",
            \"full_name\": \"$full_name\",
            \"password\": \"$password\",
            \"role\": \"$role\"
        }")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" -eq 201 ]; then
        echo -e "${GREEN}✅ Success${NC}"
        return 0
    elif [ "$http_code" -eq 400 ]; then
        echo -e "${YELLOW}⚠️  Already exists${NC}"
        return 1
    else
        echo -e "${RED}❌ Failed (HTTP $http_code)${NC}"
        echo "$body" | head -5
        return 1
    fi
}

# Check if server is running
echo "Checking if server is running..."
if ! curl -s -f "$API_URL" > /dev/null 2>&1 && ! curl -s -f "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${RED}❌ Server not responding at http://localhost:8000${NC}"
    echo ""
    echo "Please start the backend server first:"
    echo "  cd backend && ./start.sh"
    exit 1
fi

echo -e "${GREEN}✅ Server is running${NC}"
echo ""

# Create users
create_user "admin@dealership.com" "admin" "Admin User" "admin123" "admin"
create_user "manager@dealership.com" "manager" "Sales Manager" "manager123" "manager"
create_user "rep1@dealership.com" "rep1" "Sales Rep 1" "rep123" "sales_rep"
create_user "rep2@dealership.com" "rep2" "Sales Rep 2" "rep123" "sales_rep"

echo ""
echo "=================================="
echo -e "${GREEN}✅ User creation complete!${NC}"
echo ""
echo "Login Credentials:"
echo "  Admin:   username=admin,    password=admin123"
echo "  Manager: username=manager,   password=manager123"
echo "  Rep 1:   username=rep1,      password=rep123"
echo "  Rep 2:   username=rep2,      password=rep123"
echo ""
echo "Frontend: http://localhost:5173"

