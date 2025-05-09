import json
import pandas as pd
from pandas import DataFrame
from typing import Dict, Literal, Callable

from datastore import DataStore
from kafkalib import Kafka, Timeframe, Signal

StrategyFn = Callable[[DataFrame], Signal | list[Signal]]

ds = DataStore()
kafka = Kafka()
kafka_app = kafka.get_app()


class DataBuilder:
    def __init__(self, tickers: list[str]):
        self.tickers = tickers
        self.data = {}

        for tick in tickers:
            columns_with_types = {
                "ts": pd.Series(dtype="datetime64[ns]"),
                "open": pd.Series(dtype="float64"),
                "high": pd.Series(dtype="float64"),
                "low": pd.Series(dtype="float64"),
                "close": pd.Series(dtype="float64"),
                "volume": pd.Series(dtype="float64"),
                "open_interest": pd.Series(dtype="float64"),
            }

            df = pd.DataFrame(columns=columns_with_types)
            df = df.set_index("ts", inplace=True)

            self.data[tick] = df

    def add_data(
        self,
        tick: str,
        data: Dict[str, str | int | float],
    ):
        if tick not in self.data:
            raise ValueError(f"Ticker {tick} not found in data store")

        df = self.data[tick]
        new_df = pd.DataFrame([data])
        new_df.set_index("ts", inplace=True)
        df = pd.concat([df, new_df])

        self.data[tick] = df

    def get_data(self, tick: str):
        return self.data[tick]


class StrategyBuilder:
    def __init__(
        self,
        name: str,
        ticker: str,
        run_tf: Timeframe,
        strategy: StrategyFn,
        broker: Literal["upstox"],
        config: Dict[str, str | int | float] | None = None,
        init_data: DataFrame | None = None,
    ):
        self.name = name
        self.ticker = ticker
        self.run_tf: Timeframe = run_tf
        self.config = config
        self.broker = broker
        self.strategy = strategy
        self.store = DataBuilder([ticker])
        self._validate()

        if init_data is not None:
            self.init_data = init_data

        self.run()

    def _validate(self):
        if not self.name:
            raise ValueError("Strategy must be uniquely identifiable")

        if not self.strategy:
            raise NotImplementedError("Strategy function must be provided")

        if not self.broker:
            raise ValueError("Broker must be provided")

        if self.ticker is None:
            raise ValueError("Please provide a ticker")

        if self.run_tf not in ["1M", "2M", "5M", "10M", "15M", "30M", "1H", "4H", "1D"]:
            raise ValueError("Invalid time frame")

    def run(self):
        ds.add_to_priority(self.ticker)
        datafeed_topic = kafka.get_feed_topic(self.run_tf)

        with kafka_app.get_consumer() as consumer:
            consumer.subscribe([datafeed_topic.name])

            while True:
                res = consumer.poll(5)

                if res is None:
                    print(f"{self.name} No Data")
                    continue

                current_tick = res.key().decode("utf-8")  # type: ignore

                if current_tick == self.ticker:
                    print(f"{self.ticker} Data Received")
                    bar_data = res.value().decode("utf-8")  # type: ignore
                    bar_data = json.loads(bar_data)
                    self.store.add_data(current_tick, bar_data)

                    signals = self.strategy(self.store.get_data(current_tick))

                    if signals is None:
                        continue


if __name__ == "__main__":

    def strategyFn(data: pd.DataFrame):
        print("[S]: Strategy Runs")

        return [
            Signal(
                quantity=1,
                action="buy",
                type="entry",
                order_type="market",
            )
        ]

    builder = StrategyBuilder(
        name="test",
        ticker="TATASTEEL.NSE",
        run_tf="1M",
        strategy=strategyFn,
        broker="upstox",
    )
