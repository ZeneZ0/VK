from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.bot import VKBot
from backend.app.models.subscription import Subscription
from backend.app.api.dependencies import get_current_active_user
from backend.app.services.vk_service import (
    create_post, create_repost, create_comment, 
    add_like, join_group, send_message_to_self
)
from backend.app.services.statistic_service import create_statistic, update_statistic

router = APIRouter(prefix="/api/publish", tags=["publish"])

# ============= НОВЫЕ СХЕМЫ ДЛЯ МАССОВЫХ ОПЕРАЦИЙ =============

class PostItem(BaseModel):
    text: str
    attachments: List[str] = []

class PostsRequest(BaseModel):
    posts: List[str]  # список текстов постов

class RepostItem(BaseModel):
    text: str
    link: str

class RepostsRequest(BaseModel):
    reposts: List[RepostItem]

class RepostDMRequest(BaseModel):
    links: List[str]
    bot_ids: List[int]
    message: str = ""

class CommentRequest(BaseModel):
    post_link: str
    comments: List[str]  # список комментариев

class LikeRequest(BaseModel):
    links: List[str]
    likes_per_post: int = 1

class JoinGroupRequest(BaseModel):
    group_link: str
    bot_ids: List[int]  # список ID ботов для подписки

class SendToTelegramRequest(BaseModel):
    mode: str  # "fair" или "all"
    bot_ids: List[int]
    # файлы будут в FormData

# ============= СТАРЫЕ СХЕМЫ (для обратной совместимости) =============

class SinglePostRequest(BaseModel):
    text: str
    attachments: List[str] = []

class SingleRepostRequest(BaseModel):
    link: str
    message: str = ""

class SingleCommentRequest(BaseModel):
    post_link: str
    message: str

class SingleLikeRequest(BaseModel):
    link: str

class SingleJoinGroupRequest(BaseModel):
    group_link: str

class SingleMessageToSelfRequest(BaseModel):
    message: str
    attachment: str = ""


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_subscription(user: User, db: Session) -> bool:
    """Проверяет, есть ли у пользователя активная подписка"""
    if user.role == "ADMIN":
        return True
    
    subscription = db.query(Subscription).filter(Subscription.user_id == user.id).first()
    if not subscription:
        return False
    
    if subscription.is_active and subscription.end_date and subscription.end_date > datetime.now():
        return True
    
    return False


# ============= МАССОВЫЕ ЭНДПОИНТЫ (для страниц) =============

@router.post("/post")
async def publish_posts(
    request: PostsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Опубликовать несколько постов от имени всех активных ботов"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    valid_posts = [p for p in request.posts if p.strip()]
    if not valid_posts:
        raise HTTPException(status_code=400, detail="Нет валидных постов")
    
    results = []
    for bot in bots:
        for post_text in valid_posts:
            # Создаём запись в статистике
            stat = create_statistic(
                db, current_user.id, "post",
                bot_id=bot.id,
                bot_name=bot.name,
                details=post_text[:200],
                status="pending"
            )
            
            try:
                result = create_post(bot.token, post_text, [])
                
                if result["success"]:
                    update_statistic(db, stat.id, "success")
                else:
                    update_statistic(db, stat.id, "error", result.get("error"))
            except Exception as e:
                update_statistic(db, stat.id, "error", str(e))
                result = {"success": False, "error": str(e)}
            
            results.append({
                "bot_id": bot.id,
                "bot_name": bot.name,
                "post_text": post_text[:50],
                "success": result.get("success", False),
                "post_id": result.get("post_id"),
                "error": result.get("error")
            })
    
    return {
        "total_bots": len(bots),
        "total_posts": len(valid_posts),
        "total_operations": len(bots) * len(valid_posts),
        "results": results
    }


@router.post("/repost")
async def publish_reposts(
    request: RepostsRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Сделать несколько репостов от имени всех активных ботов"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    valid_reposts = [r for r in request.reposts if r.text.strip() and r.link.strip()]
    if not valid_reposts:
        raise HTTPException(status_code=400, detail="Нет валидных репостов")
    
    results = []
    for bot in bots:
        for repost in valid_reposts:
            stat = create_statistic(
                db, current_user.id, "repost_wall",
                bot_id=bot.id,
                bot_name=bot.name,
                details=f"{repost.text[:100]} | {repost.link}",
                status="pending"
            )
            
            try:
                result = create_repost(bot.token, repost.link, repost.text)
                
                if result["success"]:
                    update_statistic(db, stat.id, "success")
                else:
                    update_statistic(db, stat.id, "error", result.get("error"))
            except Exception as e:
                update_statistic(db, stat.id, "error", str(e))
                result = {"success": False, "error": str(e)}
            
            results.append({
                "bot_id": bot.id,
                "bot_name": bot.name,
                "link": repost.link[:50],
                "success": result.get("success", False),
                "repost_id": result.get("repost_id"),
                "error": result.get("error")
            })
    
    return {
        "total_bots": len(bots),
        "total_reposts": len(valid_reposts),
        "total_operations": len(bots) * len(valid_reposts),
        "results": results
    }


@router.post("/repost_dm")
async def publish_reposts_dm(
    request: RepostDMRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Сделать репосты в ЛС (в сохранённые сообщения)"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    # Получаем выбранных ботов
    bots = db.query(VKBot).filter(
        VKBot.id.in_(request.bot_ids),
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет выбранных активных ботов")
    
    valid_links = [l for l in request.links if l.strip()]
    if not valid_links:
        raise HTTPException(status_code=400, detail="Нет валидных ссылок")
    
    results = []
    for bot in bots:
        for link in valid_links:
            stat = create_statistic(
                db, current_user.id, "repost_dm",
                bot_id=bot.id,
                bot_name=bot.name,
                details=f"{request.message[:100]} | {link}",
                status="pending"
            )
            
            full_message = f"{request.message}\n{link}" if request.message else link
            
            try:
                result = send_message_to_self(bot.token, full_message, None)
                
                if result["success"]:
                    update_statistic(db, stat.id, "success")
                else:
                    update_statistic(db, stat.id, "error", result.get("error"))
            except Exception as e:
                update_statistic(db, stat.id, "error", str(e))
                result = {"success": False, "error": str(e)}
            
            results.append({
                "bot_id": bot.id,
                "bot_name": bot.name,
                "link": link[:50],
                "success": result.get("success", False),
                "message_id": result.get("message_id"),
                "error": result.get("error")
            })
    
    return {
        "total_bots": len(bots),
        "total_links": len(valid_links),
        "total_operations": len(bots) * len(valid_links),
        "results": results
    }


@router.post("/comment")
async def publish_comments(
    request: CommentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Оставить комментарии под постом (распределение между ботами)"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    valid_comments = [c for c in request.comments if c.strip()]
    if not valid_comments:
        raise HTTPException(status_code=400, detail="Нет валидных комментариев")
    
    # Распределяем комментарии между ботами
    results = []
    for i, bot in enumerate(bots):
        comment_index = i % len(valid_comments)
        comment_text = valid_comments[comment_index]
        
        stat = create_statistic(
            db, current_user.id, "comment",
            bot_id=bot.id,
            bot_name=bot.name,
            details=comment_text[:200],
            status="pending"
        )
        
        try:
            result = create_comment(bot.token, request.post_link, comment_text)
            
            if result["success"]:
                update_statistic(db, stat.id, "success")
            else:
                update_statistic(db, stat.id, "error", result.get("error"))
        except Exception as e:
            update_statistic(db, stat.id, "error", str(e))
            result = {"success": False, "error": str(e)}
        
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "comment": comment_text[:50],
            "success": result.get("success", False),
            "comment_id": result.get("comment_id"),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "total_comments": len(valid_comments),
        "results": results
    }


@router.post("/like")
async def publish_likes(
    request: LikeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Поставить лайки на несколько ссылок"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    valid_links = [l for l in request.links if l.strip()]
    if not valid_links:
        raise HTTPException(status_code=400, detail="Нет валидных ссылок")
    
    actual_likes_per_post = min(request.likes_per_post, len(bots))
    
    results = []
    for link in valid_links:
        for i in range(actual_likes_per_post):
            bot = bots[i % len(bots)]
            
            stat = create_statistic(
                db, current_user.id, "like",
                bot_id=bot.id,
                bot_name=bot.name,
                details=link[:200],
                status="pending"
            )
            
            try:
                result = add_like(bot.token, link)
                
                if result["success"]:
                    update_statistic(db, stat.id, "success")
                else:
                    update_statistic(db, stat.id, "error", result.get("error"))
            except Exception as e:
                update_statistic(db, stat.id, "error", str(e))
                result = {"success": False, "error": str(e)}
            
            results.append({
                "bot_id": bot.id,
                "bot_name": bot.name,
                "link": link[:50],
                "success": result.get("success", False),
                "error": result.get("error")
            })
    
    return {
        "total_bots": len(bots),
        "total_links": len(valid_links),
        "likes_per_post": actual_likes_per_post,
        "total_operations": len(valid_links) * actual_likes_per_post,
        "results": results
    }


@router.post("/join_group")
async def publish_join_group(
    request: JoinGroupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Подписать выбранных ботов на группу"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.id.in_(request.bot_ids),
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет выбранных активных ботов")
    
    results = []
    for bot in bots:
        stat = create_statistic(
            db, current_user.id, "subscribe",
            bot_id=bot.id,
            bot_name=bot.name,
            details=request.group_link[:200],
            status="pending"
        )
        
        try:
            result = join_group(bot.token, request.group_link)
            
            if result["success"]:
                update_statistic(db, stat.id, "success")
            else:
                update_statistic(db, stat.id, "error", result.get("error"))
        except Exception as e:
            update_statistic(db, stat.id, "error", str(e))
            result = {"success": False, "error": str(e)}
        
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result.get("success", False),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }


@router.post("/send_to_telegram")
async def send_to_telegram(
    mode: str,
    bot_ids: List[int],
    files: List[str],  # в реальности будет FormData с файлами
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Отправить файлы в Telegram"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.id.in_(bot_ids),
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет выбранных активных ботов")
    
    # TODO: реализовать отправку файлов в Telegram
    # Пока возвращаем заглушку
    
    return {
        "total_bots": len(bots),
        "mode": mode,
        "files_count": len(files),
        "message": "Функция отправки файлов в Telegram будет реализована позже"
    }


# ============= ОДИНОЧНЫЕ ЭНДПОИНТЫ (для обратной совместимости) =============

@router.post("/post/single")
async def publish_single_post(
    request: SinglePostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Опубликовать один пост от имени всех ботов (старый формат)"""
    return await publish_posts(PostsRequest(posts=[request.text]), current_user, db)


@router.post("/repost/single")
async def publish_single_repost(
    request: SingleRepostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Сделать один репост от имени всех ботов (старый формат)"""
    return await publish_reposts(RepostsRequest(reposts=[RepostItem(text=request.message, link=request.link)]), current_user, db)


@router.post("/comment/single")
async def publish_single_comment(
    request: SingleCommentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Оставить один комментарий от имени всех ботов (старый формат)"""
    return await publish_comments(CommentRequest(post_link=request.post_link, comments=[request.message]), current_user, db)


@router.post("/like/single")
async def publish_single_like(
    request: SingleLikeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Поставить один лайк от имени всех ботов (старый формат)"""
    return await publish_likes(LikeRequest(links=[request.link], likes_per_post=1), current_user, db)


@router.post("/join_group/single")
async def publish_single_join_group(
    request: SingleJoinGroupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Подписать всех ботов на группу (старый формат)"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    bot_ids = [b.id for b in bots]
    return await publish_join_group(JoinGroupRequest(group_link=request.group_link, bot_ids=bot_ids), current_user, db)


@router.post("/message_to_self")
async def publish_message_to_self(
    request: SingleMessageToSelfRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Отправить сообщение самому себе (в сохранённые)"""
    if not check_subscription(current_user, db):
        raise HTTPException(status_code=403, detail="Требуется подписка. Оформите подписку для доступа к сервису.")
    
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        stat = create_statistic(
            db, current_user.id, "message_to_self",
            bot_id=bot.id,
            bot_name=bot.name,
            details=request.message[:200],
            status="pending"
        )
        
        try:
            result = send_message_to_self(bot.token, request.message, request.attachment)
            
            if result["success"]:
                update_statistic(db, stat.id, "success")
            else:
                update_statistic(db, stat.id, "error", result.get("error"))
        except Exception as e:
            update_statistic(db, stat.id, "error", str(e))
            result = {"success": False, "error": str(e)}
        
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result.get("success", False),
            "message_id": result.get("message_id"),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }