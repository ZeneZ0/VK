import vk_api
from vk_api.exceptions import ApiError
import logging

logger = logging.getLogger(__name__)

def check_vk_token(token: str):
    """
    Проверяет валидность VK токена и возвращает информацию о владельце
    
    Returns:
        dict: {
            "valid": bool,
            "error": str | None,
            "user_info": dict | None
        }
    """
    try:
        # Создаём сессию VK с токеном
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Получаем информацию о пользователе
        # Пробуем получить базовую информацию
        user_info = vk.users.get(fields="first_name,last_name,domain,photo_50")
        
        if not user_info or len(user_info) == 0:
            return {
                "valid": False,
                "error": "Не удалось получить информацию о пользователе"
            }
        
        user = user_info[0]
        
        return {
            "valid": True,
            "user_info": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user.get("last_name", ""),
                "domain": user.get("domain", ""),
                "photo": user.get("photo_50", "")
            }
        }
        
    except ApiError as e:
        logger.error(f"VK API error: {e}")
        error_msg = str(e)
        if "Invalid access token" in error_msg or "access_token is invalid" in error_msg:
            error_msg = "Токен недействителен"
        elif "User authorization failed" in error_msg:
            error_msg = "Ошибка авторизации. Проверьте права токена"
        
        return {
            "valid": False,
            "error": error_msg
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return {
            "valid": False,
            "error": "Ошибка подключения к VK API"
        }

def get_token_display(token: str) -> str:
    """Возвращает первые 20 символов токена для отображения"""
    if len(token) > 20:
        return token[:20] + "..."
    return token

def get_token_scopes(token: str) -> list:
    """
    Пытается определить права доступа токена
    (не всегда возможно, но попробуем)
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Пробуем выполнить действия с разными правами
        scopes = []
        
        # Проверяем доступ к стене
        try:
            vk.wall.get(count=1)
            scopes.append("wall")
        except:
            pass
        
        # Проверяем доступ к фото
        try:
            vk.photos.get(count=1)
            scopes.append("photos")
        except:
            pass
        
        # Проверяем доступ к группам
        try:
            vk.groups.get(count=1)
            scopes.append("groups")
        except:
            pass
        
        # Проверяем доступ к сообщениям
        try:
            vk.messages.get(count=1)
            scopes.append("messages")
        except:
            pass
        
        return scopes
    except:
        return []