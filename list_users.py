from backend.app.core.database import SessionLocal
from backend.app.models.user import User

db = SessionLocal()
users = db.query(User).all()
print(f"Всего пользователей: {len(users)}")
for user in users:
    print(f"ID: {user.id}, Email: {user.email}, Имя: {user.username}, Роль: {user.role}")
db.close()