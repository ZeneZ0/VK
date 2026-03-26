from backend.app.core.database import engine, Base
from backend.app.models.user import User
from backend.app.models.bot import VKBot
from backend.app.models.statistic import Statistic
from backend.app.models.subscription import Subscription

def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Все таблицы созданы")

if __name__ == "__main__":
    create_tables()