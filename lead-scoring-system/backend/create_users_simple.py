"""Simple script to create test users directly via SQL."""

from app.database import engine
from sqlalchemy import text
from app.utils.auth import get_password_hash

def create_users():
    """Create test users."""
    users = [
        ("admin@dealership.com", "admin", "Admin User", "admin123", "admin"),
        ("manager@dealership.com", "manager", "Sales Manager", "manager123", "manager"),
        ("rep1@dealership.com", "rep1", "Sales Rep 1", "rep123", "sales_rep"),
        ("rep2@dealership.com", "rep2", "Sales Rep 2", "rep123", "sales_rep"),
    ]
    
    with engine.connect() as conn:
        for email, username, full_name, password, role in users:
            # Check if exists
            result = conn.execute(
                text("SELECT id FROM users WHERE email = :email OR username = :username"),
                {"email": email, "username": username}
            )
            if result.fetchone():
                print(f"- User already exists: {username}")
                continue
            
            # Create user
            hashed = get_password_hash(password)
            conn.execute(
                text("""
                    INSERT INTO users (email, username, full_name, hashed_password, role, is_active)
                    VALUES (:email, :username, :full_name, :hashed, :role, true)
                """),
                {
                    "email": email,
                    "username": username,
                    "full_name": full_name,
                    "hashed": hashed,
                    "role": role
                }
            )
            print(f"✅ Created user: {username} ({role})")
        
        conn.commit()
        print("\n✅ Test users created successfully!")

if __name__ == "__main__":
    create_users()

