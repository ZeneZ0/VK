from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from backend.app.core.database import Base

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    
    # Статус подписки
    is_active = Column(Boolean, default=False)
    
    # Данные подписки
    start_date = Column(DateTime(timezone=True), nullable=True)
    end_date = Column(DateTime(timezone=True), nullable=True)
    
    # История платежей
    last_payment_id = Column(String(200), nullable=True)
    last_payment_amount = Column(Float, nullable=True)
    last_payment_date = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Связь с пользователем
    user = relationship("User", back_populates="subscription")