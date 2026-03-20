from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Statistic(Base):
    __tablename__ = "statistics"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Тип операции
    operation_type = Column(String(50), nullable=False)  # post, repost_wall, repost_dm, comment, like, subscribe
    
    # Данные операции
    bot_id = Column(Integer, ForeignKey("vk_bots.id"), nullable=True)
    bot_name = Column(String(100), nullable=True)
    
    # Результат
    status = Column(String(20), default="pending")  # pending, success, error
    error_message = Column(Text, nullable=True)
    
    # Детали операции
    details = Column(Text, nullable=True)  # текст поста, ссылка и т.д.
    
    # Время
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Связи
    user = relationship("User", back_populates="statistics")
    bot = relationship("VKBot", back_populates="statistics")