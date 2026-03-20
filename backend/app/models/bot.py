from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class VKBot(Base):
    __tablename__ = "vk_bots"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    token = Column(String(500), nullable=False)  # зашифрованный токен
    status = Column(String(20), default="checking")  # active, error, checking
    error = Column(Text, nullable=True)
    last_check = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Информация о владельце аккаунта (из VK)
    vk_user_id = Column(Integer, nullable=True)
    vk_user_name = Column(String(200), nullable=True)
    
    # Для отображения в интерфейсе (часть токена)
    token_display = Column(String(50), nullable=True)
    
    # Связь с пользователем
    user = relationship("User", back_populates="bots")
