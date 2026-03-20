from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.orm import Session
import re

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.subscription import Subscription
from datetime import datetime

# Страницы, которые доступны без подписки
PUBLIC_PATHS = [
    r"^/$",  # лендинг
    r"^/login$",
    r"^/register$",
    r"^/static/.*",
    r"^/docs$",
    r"^/openapi.json$",
    r"^/redoc$",
    r"^/auth/.*",  # авторизация
    r"^/api/subscriptions/.*",  # подписки
    r"^/api/bots/.*",  # боты (для проверки подписки отдельно)
]

class SubscriptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Проверяем, публичный ли путь
        path = request.url.path
        for pattern in PUBLIC_PATHS:
            if re.match(pattern, path):
                return await call_next(request)
        
        # Проверяем токен
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            # Если нет токена, пропускаем (редирект на логин будет на фронте)
            return await call_next(request)
        
        token = auth_header.replace("Bearer ", "")
        
        # Получаем пользователя из токена
        try:
            from jose import jwt
            from backend.app.core.security import SECRET_KEY, ALGORITHM
            
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            
            if not email:
                return await call_next(request)
            
            db = SessionLocal()
            user = db.query(User).filter(User.email == email).first()
            
            if not user:
                db.close()
                return await call_next(request)
            
            # Администраторы имеют доступ всегда
            if user.role == "ADMIN":
                db.close()
                return await call_next(request)
            
            # Проверяем подписку
            subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
            
            has_access = False
            if subscription and subscription.is_active and subscription.end_date and subscription.end_date > datetime.now():
                has_access = True
            
            db.close()
            
            # Если нет подписки и это не публичный путь
            if not has_access and path not in ["/subscribe", "/api/subscriptions/me", "/api/subscriptions/create_payment"]:
                # Возвращаем ошибку, которую обработает фронт
                return JSONResponse(
                    status_code=status.HTTP_403_FORBIDDEN,
                    content={"detail": "Требуется подписка. Оформите подписку для доступа к сервису."}
                )
                
        except Exception as e:
            print(f"Middleware error: {e}")
            pass
        
        return await call_next(request)