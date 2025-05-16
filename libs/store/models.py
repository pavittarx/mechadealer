from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional


class User(BaseModel):
    id: int
    username: str
    email: Optional[str] = None
    name: str
    capital: float = Field(default=0)
    capital_used: float = Field(default=0)
    capital_remaining: float = Field(default=0)
    is_active: bool = Field(default=False)
    is_verified: bool = Field(default=False)
    created_at: str = Field(default="now()")
    updated_at: str = Field(default="now()")


class UserTransactions(BaseModel):
    id: int
    user_id: int
    amount: float
    type: str = Field(default="deposit")
    created_at: str


class Strategies(BaseModel):
    id: int
    name: str
    description: str
    run_tf: str
    capital: float
    capital_used: float
    capital_remaining: float
    leverage: float = Field(default=1)
    pnl: float = Field(default=0)
    unrealized_pnl: float = Field(default=0)
    realized_pnl: float = Field(default=0)
    created_at: str = Field(default="now()")


class Order(BaseModel):
    id: int
    strategy_id: int
    broker_id: str
    dt: str
    ticker: str
    quantity: float
    exit_quantity: float = Field(default=0)
    action: str
    type: str
    price: float
    order_type: str
    capital_used: float
    margin_used: float
    charges: float
    ref_id: int
    is_filled: bool = Field(default=False)
    is_cancelled: bool = Field(default=False)
    is_active: bool = Field(default=True)
    version: int = Field(default=1)
    created_at: str = Field(default="now()")
    updated_at: str = Field(default="now()")


class TradeStats(BaseModel):
    id: int
    strategy_id: int
    strategy_name: str
    order_id: int
    ticker: str
    pnl: float = Field(default=0)
