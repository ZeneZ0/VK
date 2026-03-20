import vk_api
from vk_api.exceptions import ApiError
import logging
import random
import time
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

def check_vk_token(token: str):
    """Проверяет валидность VK токена"""
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        user_info = vk.users.get(fields="first_name,last_name,domain")
        
        if not user_info:
            return {"valid": False, "error": "Не удалось получить информацию о пользователе"}
        
        user = user_info[0]
        return {
            "valid": True,
            "user_info": {
                "id": user["id"],
                "first_name": user["first_name"],
                "last_name": user.get("last_name", ""),
                "domain": user.get("domain", "")
            }
        }
    except ApiError as e:
        error_msg = str(e)
        if "Invalid access token" in error_msg:
            error_msg = "Токен недействителен"
        return {"valid": False, "error": error_msg}
    except Exception as e:
        return {"valid": False, "error": f"Ошибка: {str(e)}"}

def get_token_display(token: str) -> str:
    """Возвращает первые 20 символов токена"""
    if len(token) > 20:
        return token[:20] + "..."
    return token

# ============= НОВЫЕ МЕТОДЫ =============

def create_post(token: str, text: str, attachments: List[str] = None) -> Dict[str, Any]:
    """
    Создаёт пост на стене пользователя/группы
    
    Returns:
        dict: {"success": bool, "post_id": int, "error": str}
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        params = {"message": text}
        if attachments:
            params["attachments"] = ",".join(attachments)
        
        result = vk.wall.post(**params)
        
        return {
            "success": True,
            "post_id": result.get("post_id"),
            "error": None
        }
    except ApiError as e:
        logger.error(f"VK API error creating post: {e}")
        return {"success": False, "post_id": None, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error creating post: {e}")
        return {"success": False, "post_id": None, "error": str(e)}

def create_repost(token: str, link: str, message: str = None) -> Dict[str, Any]:
    """
    Делает репост поста
    
    Returns:
        dict: {"success": bool, "repost_id": int, "error": str}
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        params = {"object": link}
        if message:
            params["message"] = message
        
        result = vk.wall.repost(**params)
        
        return {
            "success": True,
            "repost_id": result.get("post_id"),
            "error": None
        }
    except ApiError as e:
        logger.error(f"VK API error creating repost: {e}")
        return {"success": False, "repost_id": None, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error creating repost: {e}")
        return {"success": False, "repost_id": None, "error": str(e)}

def create_comment(token: str, post_link: str, message: str) -> Dict[str, Any]:
    """
    Оставляет комментарий под постом
    
    Returns:
        dict: {"success": bool, "comment_id": int, "error": str}
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Извлекаем owner_id и post_id из ссылки
        import re
        match = re.search(r'wall(-?\d+)_(\d+)', post_link)
        if not match:
            return {"success": False, "comment_id": None, "error": "Неверный формат ссылки на пост"}
        
        owner_id = int(match.group(1))
        post_id = int(match.group(2))
        
        result = vk.wall.createComment(
            owner_id=owner_id,
            post_id=post_id,
            message=message
        )
        
        return {
            "success": True,
            "comment_id": result.get("comment_id"),
            "error": None
        }
    except ApiError as e:
        logger.error(f"VK API error creating comment: {e}")
        return {"success": False, "comment_id": None, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error creating comment: {e}")
        return {"success": False, "comment_id": None, "error": str(e)}

def add_like(token: str, link: str) -> Dict[str, Any]:
    """
    Ставит лайк на пост/фото/видео/комментарий
    
    Returns:
        dict: {"success": bool, "error": str}
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Определяем тип объекта и извлекаем ID
        import re
        
        # Пост
        match = re.search(r'wall(-?\d+)_(\d+)', link)
        if match:
            owner_id = int(match.group(1))
            item_id = int(match.group(2))
            return _add_like(vk, "post", owner_id, item_id)
        
        # Фото
        match = re.search(r'photo(-?\d+)_(\d+)', link)
        if match:
            owner_id = int(match.group(1))
            photo_id = int(match.group(2))
            return _add_like(vk, "photo", owner_id, photo_id)
        
        # Видео
        match = re.search(r'video(-?\d+)_(\d+)', link)
        if match:
            owner_id = int(match.group(1))
            video_id = int(match.group(2))
            return _add_like(vk, "video", owner_id, video_id)
        
        # Комментарий
        match = re.search(r'wall(-?\d+)_(\d+)\?reply=(\d+)', link)
        if match:
            owner_id = int(match.group(1))
            comment_id = int(match.group(3))
            return _add_like(vk, "comment", owner_id, comment_id)
        
        return {"success": False, "error": "Не удалось определить тип ссылки"}
        
    except ApiError as e:
        logger.error(f"VK API error adding like: {e}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error adding like: {e}")
        return {"success": False, "error": str(e)}

def _add_like(vk, obj_type: str, owner_id: int, item_id: int) -> Dict[str, Any]:
    """Вспомогательная функция для добавления лайка"""
    try:
        result = vk.likes.add(
            type=obj_type,
            owner_id=owner_id,
            item_id=item_id
        )
        return {"success": True, "error": None, "likes": result.get("likes")}
    except ApiError as e:
        return {"success": False, "error": str(e)}

def join_group(token: str, group_link: str) -> Dict[str, Any]:
    """
    Подписывает бота на группу
    
    Returns:
        dict: {"success": bool, "error": str}
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Извлекаем group_id из ссылки
        import re
        match = re.search(r'(?:club|public|event)(\d+)|vk\.com/([a-zA-Z0-9_.]+)', group_link)
        
        group_id = None
        if match:
            if match.group(1):
                group_id = int(match.group(1))
            else:
                # По короткому имени нужно получить ID
                screen_name = match.group(2)
                result = vk.utils.resolveScreenName(screen_name=screen_name)
                if result and result.get("type") in ["group", "page", "event"]:
                    group_id = -result["object_id"]  # группы имеют отрицательный ID
        
        if not group_id:
            return {"success": False, "error": "Не удалось определить ID группы"}
        
        vk.groups.join(group_id=group_id)
        return {"success": True, "error": None}
        
    except ApiError as e:
        logger.error(f"VK API error joining group: {e}")
        error_msg = str(e)
        if "already a member" in error_msg.lower():
            error_msg = "Бот уже подписан на эту группу"
        return {"success": False, "error": error_msg}
    except Exception as e:
        logger.error(f"Unexpected error joining group: {e}")
        return {"success": False, "error": str(e)}

def send_message_to_self(token: str, message: str, attachment: str = None) -> Dict[str, Any]:
    """
    Отправляет сообщение самому себе (в сохранённые сообщения)
    """
    try:
        vk_session = vk_api.VkApi(token=token)
        vk = vk_session.get_api()
        
        # Получаем ID текущего пользователя
        user_info = vk.users.get()[0]
        user_id = user_info["id"]
        
        params = {
            "user_id": user_id,
            "message": message,
            "random_id": int(time.time() * 1000)
        }
        
        if attachment:
            params["attachment"] = attachment
        
        result = vk.messages.send(**params)
        
        return {
            "success": True,
            "message_id": result,
            "error": None
        }
    except ApiError as e:
        logger.error(f"VK API error sending message: {e}")
        return {"success": False, "message_id": None, "error": str(e)}
    except Exception as e:
        logger.error(f"Unexpected error sending message: {e}")
        return {"success": False, "message_id": None, "error": str(e)}