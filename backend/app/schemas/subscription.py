from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubscriptionBase(BaseModel):
    is_active: bool = False

class SubscriptionResponse(SubscriptionBase):
    id: int
    user_id: int
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    last_payment_date: Optional[datetime] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    pass  # ничего не нужно, один тариф

class PaymentResponse(BaseModel):
    payment_url: str
    payment_id: str
    amount: int