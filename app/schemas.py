from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional
from decimal import Decimal

class StockBase(BaseModel):
    symbol: str
    name: str
    description: str | None = None
    sector: str | None = None

class getStock(StockBase):
    id: int
    current_price: float
    is_active: bool
    updated_at: datetime
    class Config: 
        orm_mode =True

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    name: str
    email: str
    available_balance: int
    class config:
        orm_mode =True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    id: Optional[int]= None

class StockUpdate(BaseModel):
    current_price: Decimal
    description: str | None = None



