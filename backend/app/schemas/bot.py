from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VKBotBase(BaseModel):
    name: str
    token: str

class VKBotCreate(VKBotBase):
    pass

class VKBotUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[str] = None
    error: Optional[str] = None
    last_check: Optional[datetime] = None
    vk_user_id: Optional[int] = None
    vk_user_name: Optional[str] = None
    token_display: Optional[str] = None

class VKBotResponse(BaseModel):
    id: int
    user_id: int
    name: str
    token_display: Optional[str] = None
    status: str
    error: Optional[str] = None
    last_check: Optional[datetime] = None
    vk_user_id: Optional[int] = None
    vk_user_name: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class VKBotCheckResponse(BaseModel):
    valid: bool
    error: Optional[str] = None
    user_info: Optional[dict] = None