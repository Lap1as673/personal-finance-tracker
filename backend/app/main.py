import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from .database import engine, get_db
from . import models
from .routes import transactions, subscriptions
from dotenv import load_dotenv

load_dotenv()

# Создаем таблицы
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Tracker API",
    description="API для управления личными финансами и подписками",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost", "http://localhost:80", "http://127.0.0.1"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры
app.include_router(transactions.router, prefix="/api/v1")
app.include_router(subscriptions.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "message": "Finance Tracker API", 
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
async def health(db=Depends(get_db)):
    try:
        # Проверяем подключение к БД
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "debug": os.getenv("DEBUG", "False")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }

@app.get("/api/v1/summary/overview")
async def get_overview(db=Depends(get_db)):
    """Общая сводка по финансам"""
    from sqlalchemy import func
    
    # Сумма доходов
    total_income = db.query(func.sum(models.Transaction.amount))\
        .filter(models.Transaction.type == "income")\
        .scalar() or 0
    
    # Сумма расходов
    total_expense = db.query(func.sum(models.Transaction.amount))\
        .filter(models.Transaction.type == "expense")\
        .scalar() or 0
    
    # Активные подписки
    active_subscriptions = db.query(models.Subscription)\
        .filter(models.Subscription.active == True)\
        .count()
    
    # Месячная стоимость подписок
    monthly_subs_cost = 0
    subs = db.query(models.Subscription)\
        .filter(models.Subscription.active == True)\
        .all()
    
    for sub in subs:
        if sub.billing_cycle == "monthly":
            monthly_subs_cost += sub.price
        elif sub.billing_cycle == "yearly":
            monthly_subs_cost += sub.price / 12
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense,
        "active_subscriptions": active_subscriptions,
        "monthly_subscriptions_cost": monthly_subs_cost,
        "total_transactions": db.query(models.Transaction).count()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app", 
        host=os.getenv("API_HOST", "0.0.0.0"), 
        port=int(os.getenv("API_PORT", 8000)), 
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )
