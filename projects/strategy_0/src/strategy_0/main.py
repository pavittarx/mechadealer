import pandas_ta_classic as ta
from dotenv import load_dotenv
from pandas import DataFrame
from strategylib import Signal, StrategyBuilder


def strategyFunc(data: DataFrame):
    if len(data) < 12:
        print("Insufficient data for strategy execution. Need at least 19 data points.")
        print("Available:", len(data))
        return []

    df = data.copy()
    # pandas_ta_classic re-exports `ema` over a submodule of the same name;
    # it resolves to the function at runtime.
    df["EMA_4"] = ta.ema(df["close"], length=4)  # type: ignore[operator]
    df["EMA_8"] = ta.ema(df["close"], length=8)  # type: ignore[operator]

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


def main():

    load_dotenv()
    strategy = StrategyBuilder(
        name="Short Term Growth Strategy",
        run_tf="2M",
        tickers=["IDEA.NSE"],
        broker="UPSTOX",
        strategy=strategyFunc,
    )
    strategy.run()


if __name__ == "__main__":
    main()
