from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.core.security import get_password_hash

db = SessionLocal()

# Проверяем, нет ли уже
existing = db.query(User).filter(User.email == "vladk228.sh228@yandex.ru").first()
if existing:
    print("❌ Пользователь уже есть, удаляю...")
    db.delete(existing)
    db.commit()

# Создаём нового
user = User(
    email="vladk228.sh228@yandex.ru",
    username="Vlad_Kovalev",
    hashed_password=get_password_hash("Gg7412369"),
    role="ADMIN"
)
db.add(user)
db.commit()
print("✅ Пользователь создан как ADMIN!")

db.close()