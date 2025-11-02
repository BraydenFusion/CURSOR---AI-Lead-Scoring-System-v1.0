"""Create users using pure SQL - no model imports."""

from sqlalchemy import create_engine, text
from passlib.context import CryptContext

# Database connection
DATABASE_URL = "postgresql+psycopg://postgres:postgres@localhost:5433/lead_scoring"
engine = create_engine(DATABASE_URL)

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

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
            
            # Hash password
            hashed = pwd_context.hash(password)
            
            # Create user
            conn.execute(
                text("""
                    INSERT INTO users (email, username, full_name, hashed_password, role, is_active, created_at)
                    VALUES (:email, :username, :full_name, :hashed, :role, true, NOW())
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
        print("\nLogin credentials:")
        print("Admin: username=admin, password=admin123")
        print("Manager: username=manager, password=manager123")
        print("Sales Rep 1: username=rep1, password=rep123")
        print("Sales Rep 2: username=rep2, password=rep123")

if __name__ == "__main__":
    create_users()

