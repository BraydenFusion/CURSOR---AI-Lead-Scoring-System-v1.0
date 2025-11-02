"""Script to create test users for the lead scoring system."""

from app.database import SessionLocal
from app.models.user import User, UserRole
from app.utils.auth import get_password_hash


def create_test_users():
    """Create test users with different roles."""
    db = SessionLocal()

    users = [
        {
            "email": "admin@dealership.com",
            "username": "admin",
            "full_name": "Admin User",
            "password": "admin123",
            "role": UserRole.ADMIN,
        },
        {
            "email": "manager@dealership.com",
            "username": "manager",
            "full_name": "Sales Manager",
            "password": "manager123",
            "role": UserRole.MANAGER,
        },
        {
            "email": "rep1@dealership.com",
            "username": "rep1",
            "full_name": "Sales Rep 1",
            "password": "rep123",
            "role": UserRole.SALES_REP,
        },
        {
            "email": "rep2@dealership.com",
            "username": "rep2",
            "full_name": "Sales Rep 2",
            "password": "rep123",
            "role": UserRole.SALES_REP,
        },
    ]

    for user_data in users:
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if not existing:
            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=get_password_hash(user_data["password"]),
                role=user_data["role"],
            )
            db.add(user)
            print(f"✓ Created user: {user_data['username']} ({user_data['role'].value})")
        else:
            print(f"- User already exists: {user_data['username']}")

    db.commit()
    print("\n✅ Test users created!")
    print("\nLogin credentials:")
    print("Admin: username=admin, password=admin123")
    print("Manager: username=manager, password=manager123")
    print("Sales Rep 1: username=rep1, password=rep123")
    print("Sales Rep 2: username=rep2, password=rep123")


if __name__ == "__main__":
    create_test_users()

