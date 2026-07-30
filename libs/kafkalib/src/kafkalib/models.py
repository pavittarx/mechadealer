from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, model_validator

from .typelist import FillType, OrderType, SignalAction, SignalType


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
    # Advisory only. orders_management resolves exits by looking up the
    # strategy's open orders, it never reads this field.
    position: Optional[str] = None
    limit_price: Optional[float] = None
    sl: Optional[float] = None
    tp: Optional[float] = None

    @model_validator(mode="after")
    def limit_order_should_include_price(self):
        # Was a field_validator comparing against "limit" while OrderType is
        # upper-case, so it never fired. It also ran before limit_price was
        # populated -- a field validator cannot see fields declared after it.
        if self.order_type == "LIMIT" and self.limit_price is None:
            raise ValueError("limit_price is required for LIMIT orders")

        return self


class SignalEvent(Signal):
    strategy: str
    ticker: str
    ts: str = Field(default_factory=lambda: datetime.now().isoformat())
