from pandas import DataFrame
from strategylib import StrategyBuilder, Signal


def strategyFunc(data: DataFrame):
    df = data.copy()
    df["EMA_9"] = ta.ema(df["close"], length=9)
    df["EMA_19"] = ta.ema(df["close"], length=19)

    if df.empty:
        return []

    if df["EMA_9"].iloc[-1] > df["EMA_19"].iloc[-1]:
        return [
            Signal(
                action="BUY",
                type="ENTRY",
                order_type="MARKET",
                quantity=1,
            )
        ]

    elif df["EMA_9"].iloc[-1] < df["EMA_19"].iloc[-1]:
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
