from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship  # ← ЭТО НАДО ДОБАВИТЬ
from backend.app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="USER")  # ADMIN или USER
    is_active = Column(Boolean, default=True)
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Настройки из профиля
    likes_per_post = Column(Integer, default=0)
    telegram_chat_id = Column(String, nullable=True)
    
    # Связь с ботами
    bots = relationship("VKBot", back_populates="user", cascade="all, delete-orphan")