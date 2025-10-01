from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from .. import schemas, models
from ..database import get_db

router = APIRouter(prefix="/transactions", tags=["transactions"])

@router.get("/", response_model=List[schemas.Transaction])
def get_transactions(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    transactions = db.query(models.Transaction)\
        .order_by(models.Transaction.created_at.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    return transactions

@router.post("/", response_model=schemas.Transaction)
def create_transaction(
    transaction: schemas.TransactionCreate, 
    db: Session = Depends(get_db)
):
    # Валидация типа транзакции
    if transaction.type not in ["income", "expense"]:
        raise HTTPException(
            status_code=400, 
            detail="Type must be 'income' or 'expense'"
        )
    
    db_transaction = models.Transaction(**transaction.dict())
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

@router.get("/{transaction_id}", response_model=schemas.Transaction)
def get_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction)\
        .filter(models.Transaction.id == transaction_id)\
        .first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction

@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: int, db: Session = Depends(get_db)):
    transaction = db.query(models.Transaction)\
        .filter(models.Transaction.id == transaction_id)\
        .first()
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    db.delete(transaction)
    db.commit()
    
    return {"message": "Transaction deleted successfully"}

@router.get("/summary/total")
def get_total_summary(db: Session = Depends(get_db)):
    total_income = db.query(models.Transaction)\
        .filter(models.Transaction.type == "income")\
        .with_entities(func.sum(models.Transaction.amount))\
        .scalar() or 0
    
    total_expense = db.query(models.Transaction)\
        .filter(models.Transaction.type == "expense")\
        .with_entities(func.sum(models.Transaction.amount))\
        .scalar() or 0
    
    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "balance": total_income - total_expense
    }
