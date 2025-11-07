#!/usr/bin/env python3
"""Create your sales rep account via API (works on Railway).

This script creates your account by calling the registration API endpoint.
Usage:
    python create_my_account.py
    # Or with custom credentials:
    python create_my_account.py --username brayden --password "YourSecurePass123!"
"""

import sys
import os
import argparse
import requests
import json

# Default credentials for Brayden's account
DEFAULT_USERNAME = "brayden"
DEFAULT_EMAIL = "bsaundersjones@gmail.com"
DEFAULT_PASSWORD = "Brayden@Secure2024!"
DEFAULT_FULL_NAME = "Brayden Saunders-Jones"
DEFAULT_COMPANY_ROLE = "VP Sales"

# Backend URL - change this if your backend URL is different
BACKEND_URL = os.getenv("BACKEND_URL", "https://backend-base.up.railway.app")

def create_account_via_api(
    username: str = DEFAULT_USERNAME,
    password: str = DEFAULT_PASSWORD,
    email: str = DEFAULT_EMAIL,
    full_name: str = DEFAULT_FULL_NAME,
    company_role: str = DEFAULT_COMPANY_ROLE
):
    """Create sales rep account via registration API."""
    
    api_url = f"{BACKEND_URL}/api/auth/register"
    
    payload = {
        "email": email,
        "username": username,
        "full_name": full_name,
        "password": password,
        "company_role": company_role,
        "role": "sales_rep"  # Use lowercase string value
    }
    
    print("=" * 70)
    print("🚀 Creating your Sales Rep account...")
    print("=" * 70)
    print(f"Backend URL: {BACKEND_URL}")
    print(f"Username: {username}")
    print(f"Email: {email}")
    print(f"Full Name: {full_name}")
    print(f"Company Role: {company_role}")
    print("=" * 70)
    print("\n📤 Sending registration request...")
    
    try:
        response = requests.post(
            api_url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        if response.status_code == 201:
            print("\n✅ Account created successfully!")
            print("=" * 70)
            print("\n📍 YOUR LOGIN CREDENTIALS:")
            print(f"   Username: {username}")
            print(f"   Password: {password}")
            print("=" * 70)
            print("\n🌐 LOGIN URLS:")
            print(f"   Railway: https://frontend-production-e9b2.up.railway.app/login")
            print(f"   Ventrix: https://ventrix.tech/login")
            print("=" * 70)
            print("\n📊 After login, you'll be redirected to:")
            print("   /dashboard/sales-rep")
            print("=" * 70)
            
            # Try to get the user data from response
            try:
                data = response.json()
                if "user" in data:
                    print(f"\n✅ User ID: {data['user'].get('id', 'N/A')}")
                    print(f"✅ Role: {data['user'].get('role', 'N/A')}")
            except:
                pass
            
            return True
            
        elif response.status_code == 400:
            error_data = response.json()
            error_msg = error_data.get("detail", "Unknown error")
            
            if "already exists" in error_msg.lower() or "already registered" in error_msg.lower():
                print("\n⚠️  Account already exists!")
                print("=" * 70)
                print(f"   Username '{username}' or email '{email}' is already registered.")
                print("\n💡 You can:")
                print("   1. Try logging in with these credentials")
                print("   2. Use a different username/email")
                print("   3. Reset your password if you forgot it")
                print("=" * 70)
                return False
            else:
                print(f"\n❌ Registration failed: {error_msg}")
                return False
        else:
            print(f"\n❌ Registration failed with status code: {response.status_code}")
            try:
                error_data = response.json()
                print(f"Error: {json.dumps(error_data, indent=2)}")
            except:
                print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print(f"\n❌ Cannot connect to backend at {BACKEND_URL}")
        print("\n💡 Please check:")
        print("   1. The backend is deployed and running on Railway")
        print("   2. The BACKEND_URL is correct")
        print("   3. You have internet connection")
        return False
    except requests.exceptions.Timeout:
        print(f"\n❌ Request timed out. The backend may be slow or unavailable.")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create your sales rep account via API")
    parser.add_argument("--username", default=DEFAULT_USERNAME, help=f"Username (default: {DEFAULT_USERNAME})")
    parser.add_argument("--password", default=DEFAULT_PASSWORD, help=f"Password (default: {DEFAULT_PASSWORD})")
    parser.add_argument("--email", default=DEFAULT_EMAIL, help=f"Email (default: {DEFAULT_EMAIL})")
    parser.add_argument("--full-name", default=DEFAULT_FULL_NAME, help=f"Full name (default: {DEFAULT_FULL_NAME})")
    parser.add_argument("--company-role", default=DEFAULT_COMPANY_ROLE, help=f"Company role (default: {DEFAULT_COMPANY_ROLE})")
    parser.add_argument("--backend-url", default=BACKEND_URL, help=f"Backend URL (default: {BACKEND_URL})")
    
    args = parser.parse_args()
    BACKEND_URL = args.backend_url
    
    success = create_account_via_api(
        username=args.username,
        password=args.password,
        email=args.email,
        full_name=args.full_name,
        company_role=args.company_role
    )
    
    sys.exit(0 if success else 1)

