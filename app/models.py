from .database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Enum, Float, text, Numeric
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP
from datetime import datetime
import enum


class TransactionType(str, enum.Enum):
    BUY = "BUY"
    SELL = "SELL"

class TransactionStatus(str, enum.Enum):
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    PENDING = "PENDING"

class User(Base):
    __tablename__ ="users"

    id =Column(Integer, primary_key=True, nullable=False)
    name =Column(String, nullable=False)
    email =Column(String, nullable=False)
    password =Column(String, nullable=False)
    available_balance =Column(Integer, nullable=False, server_default=text("10000"))

class Stocks(Base):
    __tablename__ ="stocks"

    id =Column(Integer, primary_key=True, nullable=False)
    name =Column(String, nullable=False)
    symbol =Column(String, nullable=False)
    description =Column(String, nullable=False, default="")
    sector =Column(String, nullable=False)
    current_price =Column(Numeric(18,4), nullable=False)
    is_active =Column(Boolean, server_default='True')
    created_at =Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)
    updated_at =Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

class Holdings(Base):
    __tablename__ = "holdings"

    id =Column(Integer, primary_key=True, nullable=False)
    user_id =Column(Integer, ForeignKey("users.id"), nullable=False)
    stock_id =Column(Integer,ForeignKey("stocks.id") ,nullable=False)
    shares =Column(Numeric(18,8), nullable=False)
    avg_buy_price =Column(Numeric(18,8), nullable=False)

class Transaction(Base):
    __tablename__ ="transactions"

    id =Column(Integer, primary_key=True, nullable=False)
    user_id =Column(Integer, ForeignKey("users.id") ,nullable=False)
    stock_id =Column(Integer, ForeignKey("stocks.id"),nullable=False)
    shares =Column(Numeric(18,8), nullable=False)
    price_per_share =Column(Float, nullable=False)
    total_amount =Column(Float, nullable=False)
    type =Column(
        Enum(TransactionType, name="transaction_type"),
        nullable=False, 
        default=TransactionType.BUY)
    status = Column(
        Enum(TransactionStatus, name="transaction_status"),
        nullable=False, 
        default=TransactionStatus.COMPLETED)
    created_at =Column(TIMESTAMP(timezone=True),server_default=text('now()'),nullable=False)

    