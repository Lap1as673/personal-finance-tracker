from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models
from ..database import get_db

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])

@router.get("/", response_model=List[schemas.Subscription])
def get_subscriptions(
    skip: int = 0, 
    limit: int = 100, 
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    query = db.query(models.Subscription)
    
    if active_only:
        query = query.filter(models.Subscription.active == True)
    
    subscriptions = query\
        .order_by(models.Subscription.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return subscriptions

@router.post("/", response_model=schemas.Subscription)
def create_subscription(
    subscription: schemas.SubscriptionCreate, 
    db: Session = Depends(get_db)
):
    db_subscription = models.Subscription(**subscription.dict())
    db.add(db_subscription)
    db.commit()
    db.refresh(db_subscription)
    return db_subscription

@router.get("/{subscription_id}", response_model=schemas.Subscription)
def get_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription)\
        .filter(models.Subscription.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    return subscription

@router.put("/{subscription_id}", response_model=schemas.Subscription)
def update_subscription(
    subscription_id: int, 
    subscription_update: schemas.SubscriptionCreate,
    db: Session = Depends(get_db)
):
    subscription = db.query(models.Subscription)\
        .filter(models.Subscription.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    # Обновляем поля
    for field, value in subscription_update.dict().items():
        setattr(subscription, field, value)
    
    db.commit()
    db.refresh(subscription)
    
    return subscription

@router.delete("/{subscription_id}")
def delete_subscription(subscription_id: int, db: Session = Depends(get_db)):
    subscription = db.query(models.Subscription)\
        .filter(models.Subscription.id == subscription_id)\
        .first()
    
    if not subscription:
        raise HTTPException(status_code=404, detail="Subscription not found")
    
    db.delete(subscription)
    db.commit()
    
    return {"message": "Subscription deleted successfully"}

@router.get("/summary/monthly")
def get_monthly_subscriptions_cost(db: Session = Depends(get_db)):
    active_subscriptions = db.query(models.Subscription)\
        .filter(models.Subscription.active == True)\
        .all()
    
    monthly_cost = 0
    yearly_cost = 0
    
    for sub in active_subscriptions:
        if sub.billing_cycle == "monthly":
            monthly_cost += sub.price
        elif sub.billing_cycle == "yearly":
            yearly_cost += sub.price
    
    return {
        "monthly_subscriptions_cost": monthly_cost,
        "yearly_subscriptions_cost": yearly_cost,
        "monthly_equivalent": monthly_cost + (yearly_cost / 12),
        "total_active_subscriptions": len(active_subscriptions)
    }
