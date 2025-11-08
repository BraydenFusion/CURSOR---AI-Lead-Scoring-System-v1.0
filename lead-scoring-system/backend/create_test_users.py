#!/usr/bin/env python3
"""
Create secure test users for the lead scoring system.

This script is safe to run multiple times. It will:
  • Upsert a set of representative accounts (admin, manager, sales reps)
  • Ensure passwords meet platform security requirements (length, complexity)
  • Populate onboarding metadata so users can log in immediately
  • Print out credentials for manual testing
"""

from __future__ import annotations

from datetime import datetime

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash


TEST_USERS = [
    {
        "email": "admin@test.ventrix.ai",
        "username": "admin_test",
        "full_name": "Test Admin",
        "password": "Admin@Test2024!",
        "role": UserRole.ADMIN.value,
        "company_role": "Head of Operations",
        "company_name": "Ventrix HQ",
        "payment_plan": "enterprise",
    },
    {
        "email": "manager@test.ventrix.ai",
        "username": "manager_test",
        "full_name": "Test Manager",
        "password": "Manager@Test2024!",
        "role": UserRole.MANAGER.value,
        "company_role": "Sales Director",
        "company_name": "Ventrix HQ",
        "payment_plan": "team",
    },
    {
        "email": "rep1@test.ventrix.ai",
        "username": "rep1_test",
        "full_name": "Test Sales Rep One",
        "password": "RepOne@Test2024!",
        "role": UserRole.SALES_REP.value,
        "company_role": "Account Executive",
        "company_name": "Ventrix HQ",
        "payment_plan": "free",
    },
    {
        "email": "rep2@test.ventrix.ai",
        "username": "rep2_test",
        "full_name": "Test Sales Rep Two",
        "password": "RepTwo@Test2024!",
        "role": UserRole.SALES_REP.value,
        "company_role": "Account Executive",
        "company_name": "Ventrix HQ",
        "payment_plan": "free",
    },
]


def create_test_users() -> None:
    """Create or update the predefined test accounts."""
    session = SessionLocal()
    created = []
    updated = []

    try:
        for user_data in TEST_USERS:
            user = (
                session.query(User)
                .filter(
                    (User.email == user_data["email"])
                    | (User.username == user_data["username"])
                )
                .first()
            )

            hashed_password = get_password_hash(user_data["password"])

            if user:
                user.email = user_data["email"]
                user.username = user_data["username"]
                user.full_name = user_data["full_name"]
                user.hashed_password = hashed_password
                user.role = user_data["role"]
                user.company_role = user_data["company_role"]
                user.company_name = user_data["company_name"]
                user.payment_plan = user_data["payment_plan"]
                user.onboarding_completed = True
                user.is_active = True
                user.updated_at = datetime.utcnow()
                updated.append(user.username)
            else:
                session.add(
                    User(
                        email=user_data["email"],
                        username=user_data["username"],
                        full_name=user_data["full_name"],
                        hashed_password=hashed_password,
                        role=user_data["role"],
                        company_role=user_data["company_role"],
                        company_name=user_data["company_name"],
                        payment_plan=user_data["payment_plan"],
                        onboarding_completed=True,
                        is_active=True,
                    )
                )
                created.append(user_data["username"])

        session.commit()

        print("✅ Test users ready!\n")
        if created:
            print("Created accounts:")
            for username in created:
                print(f"  • {username}")
            print()
        if updated:
            print("Updated existing accounts:")
            for username in updated:
                print(f"  • {username}")
            print()

        print("Login credentials (case sensitive):")
        for user_data in TEST_USERS:
            print(
                f"  • {user_data['full_name']} "
                f"[role={user_data['role']}] "
                f"username={user_data['username']} "
                f"password={user_data['password']}"
            )
    finally:
        session.close()


if __name__ == "__main__":
    create_test_users()

