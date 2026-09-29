from .. import schemas, models
from fastapi import Body, FastAPI, Response, status, HTTPException, Depends, APIRouter
from sqlalchemy.orm import Session
from ..database import get_db
from fastapi import APIRouter
from typing import List
import requests
from ..services import market_data
from .. import oauth2

router = APIRouter()

@router.get("/stocks", response_model=list[schemas.getStock])
def get_stocks(db: Session=Depends(get_db)):
    stocks = db.query(models.Stocks).all()
    if not stocks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return stocks

@router.get("/stocks/{id}", response_model=schemas.getStock)
def get_stocks_byID(id: int, db: Session=Depends(get_db)):
    stock =db.query(models.Stocks).filter(models.Stocks.id == id).first()

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
    if not stock:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Stock not Found")
    stock.is_active = False
    db.commit()
    db.refresh(stock)

    return stock

