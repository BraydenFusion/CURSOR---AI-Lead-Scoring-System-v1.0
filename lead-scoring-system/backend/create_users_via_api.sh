#!/bin/bash
# Create test users via API (for Railway deployment)

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Get backend URL from environment or prompt
if [ -z "$BACKEND_URL" ]; then
    echo -e "${YELLOW}⚠️  BACKEND_URL not set.${NC}"
    echo "Please set it:"
    echo "  export BACKEND_URL=https://your-backend.railway.app"
    echo ""
    echo "Or run:"
    echo "  BACKEND_URL=https://your-backend.railway.app ./create_users_via_api.sh"
    exit 1
fi

# Remove trailing slash if present
BACKEND_URL=${BACKEND_URL%/}

echo -e "${GREEN}🚀 Creating test users via API${NC}"
echo "Backend URL: $BACKEND_URL"
echo ""

# Function to create user
create_user() {
    local email=$1
    local username=$2
    local full_name=$3
    local password=$4
    local role=$5
    
    echo -e "${YELLOW}Creating user: $username ($role)...${NC}"
    
    response=$(curl -s -w "\n%{http_code}" -X POST "$BACKEND_URL/api/auth/register" \
        -H "Content-Type: application/json" \
        -d "{
            \"email\": \"$email\",
            \"username\": \"$username\",
            \"full_name\": \"$full_name\",
            \"password\": \"$password\",
            \"role\": \"$role\"
        }")
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" -eq 201 ]; then
        echo -e "${GREEN}✅ Created user: $username${NC}"
        echo "$body" | python3 -m json.tool 2>/dev/null || echo "$body"
    elif [ "$http_code" -eq 400 ]; then
        echo -e "${YELLOW}⚠️  User $username already exists (skipping)${NC}"
    else
        echo -e "${RED}❌ Failed to create user $username (HTTP $http_code)${NC}"
        echo "$body"
        return 1
    fi
    echo ""
}

# Create users
create_user "admin@dealership.com" "admin" "Admin User" "admin123" "admin"
create_user "manager@dealership.com" "manager" "Sales Manager" "manager123" "manager"
create_user "rep1@dealership.com" "rep1" "Sales Rep 1" "rep123" "sales_rep"
create_user "rep2@dealership.com" "rep2" "Sales Rep 2" "rep123" "sales_rep"

echo -e "${GREEN}✅ Test users creation complete!${NC}"
echo ""
echo "Login credentials:"
echo "  Admin:    username=admin,    password=admin123"
echo "  Manager:  username=manager,  password=manager123"
echo "  Sales Rep 1: username=rep1, password=rep123"
echo "  Sales Rep 2: username=rep2, password=rep123"
