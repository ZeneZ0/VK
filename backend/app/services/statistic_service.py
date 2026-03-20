from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

from backend.app.models.statistic import Statistic
from backend.app.models.user import User
from backend.app.schemas.statistic import StatisticCreate, StatisticResponse, StatisticsOverview

def create_statistic(db: Session, user_id: int, operation_type: str, **kwargs) -> Statistic:
    """Создаёт запись в статистике"""
    stat = Statistic(
        user_id=user_id,
        operation_type=operation_type,
        bot_id=kwargs.get("bot_id"),
        bot_name=kwargs.get("bot_name"),
        status=kwargs.get("status", "pending"),
        error_message=kwargs.get("error_message"),
        details=kwargs.get("details")
    )
    db.add(stat)
    db.commit()
    db.refresh(stat)
    return stat

def update_statistic(db: Session, stat_id: int, status: str, error_message: str = None):
    """Обновляет статус операции"""
    stat = db.query(Statistic).filter(Statistic.id == stat_id).first()
    if stat:
        stat.status = status
        if error_message:
            stat.error_message = error_message
        db.commit()
    return stat

def get_user_statistics(
    db: Session, 
    user_id: int, 
    operation_type: Optional[str] = None,
    date_start: Optional[datetime] = None,
    date_end: Optional[datetime] = None,
    limit: int = 100,
    offset: int = 0
) -> List[Statistic]:
    """Получить статистику пользователя с фильтрами"""
    query = db.query(Statistic).filter(Statistic.user_id == user_id)
    
    if operation_type and operation_type != "all":
        query = query.filter(Statistic.operation_type == operation_type)
    
    if date_start:
        query = query.filter(Statistic.created_at >= date_start)
    
    if date_end:
        query = query.filter(Statistic.created_at <= date_end)
    
    return query.order_by(Statistic.created_at.desc()).offset(offset).limit(limit).all()

def get_statistics_overview(db: Session, user_id: int, date_start: Optional[datetime] = None, date_end: Optional[datetime] = None) -> StatisticsOverview:
    """Получить сводку статистики"""
    query = db.query(Statistic).filter(Statistic.user_id == user_id)
    
    if date_start:
        query = query.filter(Statistic.created_at >= date_start)
    if date_end:
        query = query.filter(Statistic.created_at <= date_end)
    
    total = query.count()
    successful = query.filter(Statistic.status == "success").count()
    failed = query.filter(Statistic.status == "error").count()
    
    posts = query.filter(Statistic.operation_type == "post").count()
    reposts_wall = query.filter(Statistic.operation_type == "repost_wall").count()
    reposts_dm = query.filter(Statistic.operation_type == "repost_dm").count()
    comments = query.filter(Statistic.operation_type == "comment").count()
    likes = query.filter(Statistic.operation_type == "like").count()
    subscribes = query.filter(Statistic.operation_type == "subscribe").count()
    
    success_rate = (successful / total * 100) if total > 0 else 0
    
    return StatisticsOverview(
        total_operations=total,
        successful=successful,
        failed=failed,
        posts_count=posts,
        reposts_wall_count=reposts_wall,
        reposts_dm_count=reposts_dm,
        comments_count=comments,
        likes_count=likes,
        subscribes_count=subscribes,
        success_rate=round(success_rate, 1)
    )