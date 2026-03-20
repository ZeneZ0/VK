from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class StatisticBase(BaseModel):
    operation_type: str
    bot_id: Optional[int] = None
    bot_name: Optional[str] = None
    status: str = "pending"
    error_message: Optional[str] = None
    details: Optional[str] = None

class StatisticCreate(StatisticBase):
    user_id: int

class StatisticResponse(StatisticBase):
    id: int
    user_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True

class StatisticsOverview(BaseModel):
    total_operations: int
    successful: int
    failed: int
    posts_count: int
    reposts_wall_count: int
    reposts_dm_count: int
    comments_count: int
    likes_count: int
    subscribes_count: int
    success_rate: float