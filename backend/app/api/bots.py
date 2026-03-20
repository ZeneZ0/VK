from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from typing import List

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.models.bot import VKBot
from backend.app.schemas.bot import VKBotCreate, VKBotResponse, VKBotUpdate, VKBotCheckResponse
from backend.app.api.dependencies import get_current_active_user
from backend.app.services.vk_service import check_vk_token, get_token_display

router = APIRouter(prefix="/api/bots", tags=["bots"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("", response_model=List[VKBotResponse])
async def get_bots(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить список всех ботов текущего пользователя"""
    bots = db.query(VKBot).filter(VKBot.user_id == current_user.id).all()
    return bots

@router.post("", response_model=VKBotResponse)
async def create_bot(
    bot_data: VKBotCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Создать нового бота"""
    # Проверяем лимит (максимум 48 ботов)
    bots_count = db.query(VKBot).filter(VKBot.user_id == current_user.id).count()
    if bots_count >= 48:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Достигнут лимит ботов (48). Оформите подписку для увеличения лимита"
        )
    
    # Проверяем токен через VK API
    check_result = check_vk_token(bot_data.token)
    
    # Создаём бота
    new_bot = VKBot(
        user_id=current_user.id,
        name=bot_data.name,
        token=bot_data.token,
        token_display=get_token_display(bot_data.token),
        status="active" if check_result["valid"] else "error",
        error=check_result.get("error") if not check_result["valid"] else None,
        last_check=func.now()
    )
    
    if check_result["valid"] and check_result.get("user_info"):
        new_bot.vk_user_id = check_result["user_info"]["id"]
        new_bot.vk_user_name = f"{check_result['user_info']['first_name']} {check_result['user_info'].get('last_name', '')}"
    
    db.add(new_bot)
    db.commit()
    db.refresh(new_bot)
    
    return new_bot

@router.delete("/{bot_id}")
async def delete_bot(
    bot_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Удалить бота"""
    bot = db.query(VKBot).filter(
        VKBot.id == bot_id,
        VKBot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    db.delete(bot)
    db.commit()
    
    return {"message": "Бот удалён"}

@router.post("/{bot_id}/check", response_model=VKBotCheckResponse)
async def check_bot(
    bot_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Проверить валидность токена бота"""
    bot = db.query(VKBot).filter(
        VKBot.id == bot_id,
        VKBot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    # Проверяем токен
    check_result = check_vk_token(bot.token)
    
    # Обновляем статус бота
    bot.status = "active" if check_result["valid"] else "error"
    bot.error = check_result.get("error") if not check_result["valid"] else None
    bot.last_check = func.now()
    
    if check_result["valid"] and check_result.get("user_info"):
        bot.vk_user_id = check_result["user_info"]["id"]
        bot.vk_user_name = f"{check_result['user_info']['first_name']} {check_result['user_info'].get('last_name', '')}"
    
    db.commit()
    db.refresh(bot)
    
    return VKBotCheckResponse(
        valid=check_result["valid"],
        error=check_result.get("error"),
        user_info=check_result.get("user_info")
    )

@router.put("/{bot_id}", response_model=VKBotResponse)
async def update_bot(
    bot_id: int,
    bot_data: VKBotUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Обновить информацию о боте"""
    bot = db.query(VKBot).filter(
        VKBot.id == bot_id,
        VKBot.user_id == current_user.id
    ).first()
    
    if not bot:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Бот не найден"
        )
    
    if bot_data.name is not None:
        bot.name = bot_data.name
    
    db.commit()
    db.refresh(bot)
    
    return bot