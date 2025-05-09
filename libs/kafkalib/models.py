from datetime import datetime
from typing import Literal, Optional
from pydantic import BaseModel
from pydantic import field_validator


SignalAction = Literal["buy", "sell"]
SignalType = Literal["entry", "exit"]
OrderType = Literal["market", "limit"]
FillType = Literal["all", "available"]


class DataEvent(BaseModel):
    ticker: str
    ts: datetime
    open: float
    low: float
    high: float
    close: float
    volume: int
    oi: float


class SignalEvent(BaseModel):
    strategy: str
    ticker: str
    quantity: float
    action: SignalAction
    type: SignalType
    order_type: OrderType
    fill_type: Optional[FillType]
    # Used to identify the position to exit
    position: Optional[str]
    price: Optional[float]
    sl: Optional[float]
    tp: Optional[float]

    @field_validator("type")
    def exit_signal_should_include_position(cls, v: SignalType, info):
        if v == "exit" and info.data.get("position") is None:
            raise ValueError("Position is required for exit signals")

        return v

    @field_validator("order_type")
    def limit_order_type_should_include_price(cls, v: OrderType, info):
        if v == "limit" and info.data.get("price") is None:
            raise ValueError("Price is required for limit orders")

        return v
