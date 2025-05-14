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
    created_at: str = Field(default="now()")
    updated_at: str = Field(default="now()")
    is_active: bool = Field(default=False)
    is_verified: bool = Field(default=False)


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
    unrealized_pnl: float = Field(default=0)
    realized_pnl: float = Field(default=0)
    created_at: str = Field(default="now()")
