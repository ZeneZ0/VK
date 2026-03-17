from backend.app.core.database import engine, Base
from backend.app.models.user import User

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Таблицы созданы")

if __name__ == "__main__":
    create_tables()