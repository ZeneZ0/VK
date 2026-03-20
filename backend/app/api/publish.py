from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.bot import VKBot
from backend.app.api.dependencies import get_current_active_user
from backend.app.services.vk_service import create_post, create_repost, create_comment, add_like, join_group, send_message_to_self

router = APIRouter(prefix="/api/publish", tags=["publish"])

# Схемы запросов
class PostRequest(BaseModel):
    text: str
    attachments: List[str] = []

class RepostRequest(BaseModel):
    link: str
    message: str = ""

class CommentRequest(BaseModel):
    post_link: str
    message: str

class LikeRequest(BaseModel):
    link: str

class JoinGroupRequest(BaseModel):
    group_link: str

class MessageToSelfRequest(BaseModel):
    message: str
    attachment: str = ""

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/post")
async def publish_post(
    request: PostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Опубликовать пост от имени всех активных ботов"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        result = create_post(bot.token, request.text, request.attachments)
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result["success"],
            "post_id": result.get("post_id"),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }

@router.post("/repost")
async def publish_repost(
    request: RepostRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Сделать репост от имени всех активных ботов"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        result = create_repost(bot.token, request.link, request.message)
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result["success"],
            "repost_id": result.get("repost_id"),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }

@router.post("/comment")
async def publish_comment(
    request: CommentRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Оставить комментарий от имени всех активных ботов"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        result = create_comment(bot.token, request.post_link, request.message)
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result["success"],
            "comment_id": result.get("comment_id"),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }

@router.post("/like")
async def publish_like(
    request: LikeRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Поставить лайк от имени всех активных ботов"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        result = add_like(bot.token, request.link)
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result["success"],
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }

@router.post("/join_group")
async def publish_join_group(
    request: JoinGroupRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Подписать ботов на группу"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        result = join_group(bot.token, request.group_link)
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result["success"],
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }

@router.post("/message_to_self")
async def publish_message_to_self(
    request: MessageToSelfRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Отправить сообщение самому себе (в сохранённые)"""
    bots = db.query(VKBot).filter(
        VKBot.user_id == current_user.id,
        VKBot.status == "active"
    ).all()
    
    if not bots:
        raise HTTPException(status_code=400, detail="Нет активных ботов")
    
    results = []
    for bot in bots:
        result = send_message_to_self(bot.token, request.message, request.attachment)
        results.append({
            "bot_id": bot.id,
            "bot_name": bot.name,
            "success": result["success"],
            "message_id": result.get("message_id"),
            "error": result.get("error")
        })
    
    return {
        "total_bots": len(bots),
        "results": results
    }