from .. import schemas, models
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi import APIRouter
from typing import List
import requests
from ..services import market_data
from .. import oauth2
from decimal import Decimal

router = APIRouter()

@router.get("/stocks", response_model=list[schemas.getStock])
def get_stocks(db: Session=Depends(get_db)):
    stocks = db.query(models.Stocks.is_active == True).all()
    if not stocks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return stocks

@router.get("/stocks/{id}", response_model=schemas.getStock)
def get_stocks_byID(id: int, db: Session=Depends(get_db)):
    stock =db.query(models.Stocks).filter(models.Stocks.id == id, 
                                          models.Stocks.is_active == True).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Stock not found")
    return stock

@router.post("/stocks", response_model=schemas.getStock, status_code=status.HTTP_201_CREATED)
def create_stock(
    payload: schemas.StockBase,
    db: Session = Depends(get_db),
    current_user=Depends(oauth2.get_current_user),
    ):
    existing = db.query(models.Stocks).filter(models.Stocks.symbol == payload.symbol).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Stock symbol already exists")

    try:
        data = market_data.fetch_stock_data(payload.symbol)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except requests.RequestException:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Failed to reach market data provider")

    new_stock = models.Stocks(**data, description=payload.description or "No description available")
    db.add(new_stock)
    db.commit()
    db.refresh(new_stock)
    return new_stock

@router.put("/stocks/{id}", response_model=schemas.getStock)
def update_stock(id: int,
                 payload: schemas.StockUpdate,
                 db: Session =Depends(get_db),
                 current_user =Depends(oauth2.get_current_user)):
    
    stock =db.query(models.Stocks).filter(models.Stocks.id == id).first()
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock not found")
    
    stock.current_price = payload.current_price
    stock.description = payload.description
    db.commit()
    db.refresh(stock)

    return stock

@router.delete("/stocks/{id}", response_model=schemas.getStock)
def delete_stock(id: int,
                 db: Session=Depends(get_db),
                 current_user =Depends(oauth2.get_current_user)):
    stock = db.query(models.Stocks).filter(models.Stocks.id == id).first()
    if not stock or not stock.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock not Found")
    stock.is_active = False
    db.commit()
    db.refresh(stock)

    return stock

@router.post("/stocks/{stock_id}/purchase", status_code=status.HTTP_201_CREATED, response_model=schemas.TransactionOut)
def purchase_stock(stock_id: int,
                   data: schemas.PurchaseRequest,
                   db: Session=Depends(get_db),
                   current_user =Depends(oauth2.get_current_user)):
    stock =db.query(models.Stocks).filter(models.Stocks.id == stock_id,
                                          models.Stocks.is_active == True).first()
    
    user =db.query(models.User).filter(models.User.id == current_user.id).first()

    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock not found")

    purchase_amount = stock.current_price * data.shares
    if user.available_balance >= purchase_amount:
        user.available_balance -= purchase_amount
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Insufficient Balance")

    holding =db.query(models.Holdings).filter(models.Holdings.user_id == current_user.id,
                                              models.Holdings.stock_id == stock_id).first()
    if holding:
        total_shares =holding.shares + data.shares
        new_avg_price =(holding.shares * holding.avg_buy_price + data.shares * stock.current_price)/total_shares
        holding.shares =total_shares
        holding.avg_buy_price =new_avg_price
    else:
        new_holding =models.Holdings(user_id =current_user.id,
                                     stock_id =stock_id,
                                     shares =data.shares,
                                     avg_buy_price =stock.current_price)
        db.add(new_holding)

    new_transaction =models.Transaction(
                                        user_id =current_user.id,
                                        stock_id =stock_id,
                                        shares =data.shares,
                                        price_per_share =stock.current_price,
                                        total_amount =purchase_amount,
                                        type =models.TransactionType.BUY,
                                        status =models.TransactionStatus.COMPLETED
                                        )
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction

@router.get("/stocks/receipt/{transaction_id}", response_model=schemas.Receipt)
def stock_receipt(transaction_id: int,
                  db: Session=Depends(get_db),
                  current_user =Depends(oauth2.get_current_user)):
    # transaction now has: shares, price, total_amount, stock_id=3, etc.
    transaction =db.query(models.Transaction).filter(models.Transaction.id == transaction_id).first()
    if not transaction: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Transaction not Found")

    if transaction.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail=f"You are not authorized to view this receipt")
    # stock now has: symbol="AAPL", name="Apple Inc.", etc.
    stock =db.query(models.Stocks).filter(models.Stocks.id == transaction.stock_id).first()

    #combining both the queries
    result ={
        "transaction_id": transaction.id,
        "symbol": stock.symbol,
        "name": stock.name,
        "shares": transaction.shares,
        "price_per_share": transaction.price_per_share,
        "total_amount": transaction.total_amount,
        "type": transaction.type,
        "status": transaction.status,
        "created_at": transaction.created_at
    }
    return result
    


    
    
    
    
    
        

    
