from app.database import SessionLocal
from app.models import User
from app.auth import get_password_hash

db = SessionLocal()
user = db.query(User).filter(User.username == 'admin_test2').first()
if user:
    user.hashed_password = get_password_hash('12345678')
    db.commit()
    print('Updated')
else:
    new_user = User(username='admin_test2', hashed_password=get_password_hash('12345678'), email='test@example.com')
    db.add(new_user)
    db.commit()
    print('Created')
db.close()
