from typing import Literal

Timeframe = Literal["1M", "2M", "5M", "10M", "15M", "30M", "1H", "4H", "6H", "8H"]
SignalAction = Literal["BUY", "SELL"]
SignalType = Literal["ENTRY", "EXIT", "SL", "TP"]
OrderType = Literal["MARKET", "LIMIT", "SL", "SL-M"]
FillType = Literal["ALL", "AVAILABLE"]
