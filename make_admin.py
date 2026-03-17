from backend.app.core.database import SessionLocal
from backend.app.models.user import User

db = SessionLocal()

user = db.query(User).filter(User.email == "vladk228.sh228@yandex.ru").first()

if user:
    user.role = "ADMIN"
    db.commit()
    print(f"✅ Пользователь {user.email} теперь ADMIN!")
else:
    print("❌ Пользователь не найден")

db.close()