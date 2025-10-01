from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Transaction Schemas
class TransactionBase(BaseModel):
    description: str
    amount: float
    type: str  # 'income' or 'expense'
    category: Optional[str] = "other"

class TransactionCreate(TransactionBase):
    pass

class Transaction(TransactionBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# Subscription Schemas
class SubscriptionBase(BaseModel):
    name: str
    price: float
    currency: Optional[str] = "USD"
    billing_cycle: Optional[str] = "monthly"
    active: Optional[bool] = True
    next_payment: Optional[datetime] = None

class SubscriptionCreate(SubscriptionBase):
    pass

class Subscription(SubscriptionBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
