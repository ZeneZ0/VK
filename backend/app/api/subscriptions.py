from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.subscription import Subscription
from backend.app.schemas.subscription import SubscriptionResponse, PaymentResponse
from backend.app.api.dependencies import get_current_active_user
from backend.app.services.yoomoney_service import create_payment, SUBSCRIPTION_PRICE

router = APIRouter(prefix="/api/subscriptions", tags=["subscriptions"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def has_active_subscription(user: User, db: Session) -> bool:
    """Проверяет, есть ли у пользователя активная подписка или он ADMIN"""
    if user.role == "ADMIN":
        return True
    
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not subscription:
        return False
    
    if subscription.is_active and subscription.end_date and subscription.end_date > datetime.now():
        return True
    
    return False

@router.get("/me", response_model=SubscriptionResponse)
async def get_my_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить информацию о подписке текущего пользователя"""
    subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
    
    if not subscription:
        subscription = Subscription(
            user_id=current_user.id,
            is_active=False
        )
        db.add(subscription)
        db.commit()
        db.refresh(subscription)
    
    return subscription

@router.post("/create_payment", response_model=PaymentResponse)
async def create_payment_link(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создать ссылку для оплаты подписки"""
    # Для ADMIN не нужна подписка
    if current_user.role == "ADMIN":
        raise HTTPException(status_code=400, detail="Администраторам не требуется подписка")
    
    result = create_payment(current_user.id, current_user.email)
    
    return {
        "payment_url": result["payment_url"],
        "payment_id": result["payment_id"],
        "amount": result["amount"]
    }

@router.post("/webhook")
async def payment_webhook(request_data: dict):
    """Webhook для приёма уведомлений от ЮMoney"""
    notification_type = request_data.get("notification_type")
    label = request_data.get("label")
    amount = request_data.get("amount")
    
    if notification_type != "p2p-incoming":
        return {"status": "ignored"}
    
    # Парсим label (формат: sub_{user_id}_{timestamp}_{uuid})
    parts = label.split("_")
    if len(parts) >= 2 and parts[0] == "sub":
        try:
            user_id = int(parts[1])
        except ValueError:
            return {"status": "error", "message": "Invalid user_id"}
        
        # Проверяем сумму
        amount_float = float(amount)
        if amount_float != SUBSCRIPTION_PRICE:
            return {"status": "error", "message": "Invalid amount"}
        
        # Обновляем подписку в БД
        db = next(get_db())
        subscription = db.query(Subscription).filter(Subscription.user_id == user_id).first()
        
        if not subscription:
            subscription = Subscription(user_id=user_id)
            db.add(subscription)
        
        subscription.is_active = True
        subscription.start_date = datetime.now()
        subscription.end_date = datetime.now() + timedelta(days=30)
        subscription.last_payment_id = label
        subscription.last_payment_amount = amount_float
        subscription.last_payment_date = datetime.now()
        
        db.commit()
        
        return {"status": "success"}
    
    return {"status": "error", "message": "Invalid label"}

@router.get("/check")
async def check_subscription(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Проверить, есть ли доступ к сервису"""
    has_access = has_active_subscription(current_user, db)
    
    # Если подписка истекла, обновляем статус
    if not has_access and current_user.role != "ADMIN":
        subscription = db.query(Subscription).filter(Subscription.user_id == current_user.id).first()
        if subscription and subscription.is_active and subscription.end_date <= datetime.now():
            subscription.is_active = False
            db.commit()
    
    return {
        "has_access": has_access,
        "is_admin": current_user.role == "ADMIN",
        "message": None if has_access else "Оформите подписку для доступа к сервисам"
    }