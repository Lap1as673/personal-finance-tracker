from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from .database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'income' or 'expense'
    category = Column(String, default="other")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Subscription(Base):
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float, nullable=False)
    currency = Column(String, default="USD")
    billing_cycle = Column(String, default="monthly")  # monthly, yearly
    active = Column(Boolean, default=True)
    next_payment = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
