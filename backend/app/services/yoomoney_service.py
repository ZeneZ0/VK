import requests
import uuid
import hashlib
import time
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Настройки ЮMoney (замени на свои)
YOOMONEY_RECEIVER = "4100119497392868"  # Номер кошелька или ID магазина
YOOMONEY_SECRET = "your_secret_key"  # Секретный ключ для уведомлений
YOOMONEY_URL = "https://yoomoney.ru/quickpay/confirm.xml"

# Цена подписки
SUBSCRIPTION_PRICE = 400

def create_payment(user_id: int, user_email: str) -> Dict[str, Any]:
    """
    Создаёт ссылку на оплату через ЮMoney
    
    Returns:
        dict: {"payment_url": str, "payment_id": str, "amount": int}
    """
    # Генерируем уникальный ID платежа
    payment_id = f"sub_{user_id}_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    # Создаём ссылку на оплату
    params = {
        "receiver": YOOMONEY_RECEIVER,
        "quickpay-form": "shop",
        "targets": f"Подписка VK Manager на 30 дней",
        "sum": SUBSCRIPTION_PRICE,
        "label": payment_id,
        "comment": f"Подписка для {user_email}",
        "successURL": "https://ваш-сайт.ru/subscription/success",  # Замени на свой
        "need-fio": "false",
        "need-email": "false",
        "need-phone": "false",
        "need-address": "false"
    }
    
    payment_url = f"{YOOMONEY_URL}?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    return {
        "payment_url": payment_url,
        "payment_id": payment_id,
        "amount": SUBSCRIPTION_PRICE
    }

def verify_payment(payment_id: str) -> Optional[Dict[str, Any]]:
    """Проверяет статус платежа"""
    # Здесь будет логика проверки платежа
    # В реальном проекте нужно использовать webhook от ЮMoney
    return {"valid": True}

def generate_notification_signature(params: dict, secret: str) -> str:
    """Генерирует подпись для уведомления от ЮMoney"""
    notification_type = params.get("notification_type")
    operation_id = params.get("operation_id")
    amount = params.get("amount")
    currency = params.get("currency")
    datetime_val = params.get("datetime")
    sender = params.get("sender")
    codepro = params.get("codepro")
    label = params.get("label")
    
    sha_str = f"{notification_type}&{operation_id}&{amount}&{currency}&{datetime_val}&{sender}&{codepro}&{secret}&{label}"
    return hashlib.sha256(sha_str.encode()).hexdigest()