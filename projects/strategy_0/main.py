from pandas import DataFrame
from strategylib import StrategyBuilder, Signal
import pandas_ta as ta


def strategyFunc(data: DataFrame):
    if len(data) < 12:
        print("Insufficient data for strategy execution. Need at least 19 data points.")
        print("Available:", len(data))
        return []

    df = data.copy()
    df["EMA_4"] = ta.ema(df["close"], length=4)
    df["EMA_8"] = ta.ema(df["close"], length=8)

    if df.empty:
        return []

    print("DX:", df)

    if df["EMA_4"].iloc[-1] > df["EMA_8"].iloc[-1]:
        return [
            Signal(
                action="BUY",
                type="ENTRY",
                order_type="MARKET",
                quantity=1,
            )
        ]

    elif df["EMA_8"].iloc[-1] < df["EMA_4"].iloc[-1]:
        return [
            Signal(
                action="SELL",
                type="EXIT",
                order_type="MARKET",
                quantity=1,
            )
        ]


strategy = StrategyBuilder(
    name="Short Term Growth Strategy",
    run_tf="2M",
    tickers=["IDEA.NSE"],
    broker="UPSTOX",
    strategy=strategyFunc,
)
strategy.run()
