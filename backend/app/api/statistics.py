from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from backend.app.core.database import SessionLocal
from backend.app.models.user import User
from backend.app.api.dependencies import get_current_active_user
from backend.app.services.statistic_service import (
    get_user_statistics, get_statistics_overview
)
from backend.app.schemas.statistic import StatisticResponse, StatisticsOverview

router = APIRouter(prefix="/api/statistics", tags=["statistics"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/overview", response_model=StatisticsOverview)
async def get_overview(
    date_start: Optional[str] = Query(None, description="Дата начала (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="Дата окончания (YYYY-MM-DD)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить сводку статистики"""
    start = datetime.fromisoformat(date_start) if date_start else None
    end = datetime.fromisoformat(date_end) if date_end else None
    
    return get_statistics_overview(db, current_user.id, start, end)

@router.get("/history", response_model=list[StatisticResponse])
async def get_history(
    operation_type: Optional[str] = Query("all", description="Тип операции"),
    date_start: Optional[str] = Query(None, description="Дата начала (YYYY-MM-DD)"),
    date_end: Optional[str] = Query(None, description="Дата окончания (YYYY-MM-DD)"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Получить историю операций с пагинацией"""
    start = datetime.fromisoformat(date_start) if date_start else None
    end = datetime.fromisoformat(date_end) if date_end else None
    offset = (page - 1) * limit
    
    statistics = get_user_statistics(
        db, current_user.id, operation_type, start, end, limit, offset
    )
    
    return statistics