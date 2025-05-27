from pandas import DataFrame
from strategylib import StrategyBuilder, Signal


def strategyFunc(data: DataFrame):
    print("Running strategyFunc")
    print(data)


strategy = StrategyBuilder(
    name="strategy_0",
    run_tf="2M",
    tickers=["IDEA.NSE"],
    broker="UPSTOX",
    strategy=strategyFunc,
)
strategy.run()


