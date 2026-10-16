from app.database import SessionLocal
from app.models import User, UserRole
from app.auth import get_password_hash

def create_first_admin():
    db = SessionLocal()
    existing_user = db.query(User).filter(User.username == "admin").first()
    
    if not existing_user:
        new_admin = User(
            username="admin",
            email="admin@school.com",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(new_admin)
        db.commit()
        print("Super Admin ban gaya hai! Username: admin, Password: admin123")
    else:
        print("Admin user pehle se maujood hai.")

    db.close()

if __name__ == "__main__":
    create_first_admin()
