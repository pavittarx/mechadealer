from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from pydantic import field_validator
from kafkalib.typelist import SignalAction, SignalType, OrderType, FillType


class DataEvent(BaseModel):
    ticker: str
    ts: datetime
    open: float
    low: float
    high: float
    close: float
    volume: int
    oi: float


class Signal(BaseModel):
    quantity: float
    action: SignalAction
    type: SignalType
    order_type: OrderType
    fill_type: Optional[FillType] = None
    # Used to identify the position to exit
    position: Optional[str] = None
    limit_price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None

    @field_validator("type")
    def exit_signal_should_include_position(cls, v: SignalType, info):
        if v == "exit" and info.data.get("position") is None:
            raise ValueError("Position is required for exit signals")

        return v

    @field_validator("order_type")
    def limit_order_type_should_include_price(cls, v: OrderType, info):
        if v == "limit" and info.data.get("limit_price") is None:
            raise ValueError("Price is required for limit orders")

        return v


class SignalEvent(Signal):
    strategy: str
    ticker: str
    ts: datetime = Field(default_factory=datetime.now)
