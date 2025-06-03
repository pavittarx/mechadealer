import json
import pandas as pd
from pandas import DataFrame
from typing import Dict, Literal, Callable, Optional
from pydantic import BaseModel
from pandantic import Pandantic

from datastore import DataStore
from kafkalib import Kafka, Timeframe, Signal, SignalEvent, Topics
from storelib import Store, Strategy
from .data_builder import DataBuilder


StrategyFn = Callable[[DataFrame], Signal | list[Signal] | None]

ds = DataStore()
kafka = Kafka()
kafka_app = kafka.get_app()
store = Store()


class StrategyConfig(BaseModel):
    name: str
    tickers: str | list[str]
    run_tf: Timeframe
    broker: Literal["UPSTOX"]


class StrategyBuilder:
    def __init__(
        self,
        name: str,
        tickers: str | list[str],
        run_tf: Timeframe,
        broker: Literal["UPSTOX"],
        strategy: StrategyFn,
        init_data: Optional[DataFrame | Dict[str, DataFrame]] = None,
    ):
        if isinstance(tickers, str):
            tickers = [tickers]

        self.store = DataBuilder(tickers)
        self.strategy = strategy
        self.config = StrategyConfig(
            name=name,
            tickers=tickers,
            run_tf=run_tf,
            broker=broker,
        )

        self._add_tickers_to_priority()
        strategyConfig = store.get_strategy(strategy_name=name)

        if strategyConfig is None:
            store.create_strategy(
                Strategy(
                    name=name,
                    description="",
                    run_tf=run_tf,
                    capital=0,
                    capital_remaining=0,
                )
            )

        if init_data is not None:
            self._validate_init_data(init_data)
            self._add_data_to_store(init_data)
            self.init_data = init_data

        self._remove_tickers_from_priority()

    def _add_tickers_to_priority(self):
        for tick in self.config.tickers:
            ds.add_to_priority(tick)

    def _validate_init_data(self, init_data: DataFrame | Dict[str, DataFrame]):
        if init_data is not None:
            if isinstance(init_data, DataFrame):
                req_columns = {"ts", "open", "high", "low", "close", "volume"}

                if not req_columns.issubset(init_data.columns):
                    raise ValueError(f"DataFrame must contain columns: {req_columns}")

            if isinstance(init_data, Dict):
                for tick in init_data.keys():
                    if tick not in self.store.tickers:
                        raise ValueError(f"Ticker {tick} not found in data store")
                    else:
                        df: DataFrame = init_data[tick]
                        self._validate_init_data(df)

    def _add_data_to_store(self, init_data: DataFrame | Dict[str, DataFrame]):
        if isinstance(init_data, DataFrame) and isinstance(self.config.tickers, str):
            init_data.set_index("ts", inplace=True)
            self.store.init_ticker_data(self.config.tickers, init_data)

        if isinstance(init_data, Dict):
            for tick in self.config.tickers:
                df = init_data[tick]
                df.set_index("ts", inplace=True)
                self.store.init_ticker_data(tick, df)

    def _remove_tickers_from_priority(self):
        for tick in self.config.tickers:
            ds.remove_from_priority(tick)

    def run(self):
        datafeed_topic = kafka.get_feed_topic(self.config.run_tf)

        with kafka_app.get_consumer() as consumer:
            consumer.subscribe([datafeed_topic.name])

            while True:
                res = consumer.poll(5)

                if res is None:
                    print(f"{self.config.name}: No Data")
                    continue

                current_tick = res.key().decode("utf-8")  # type: ignore

                if current_tick in self.config.tickers:
                    bar_data = res.value().decode("utf-8")  # type: ignore
                    bar_data = json.loads(bar_data)
                    self.store.add_data(current_tick, bar_data)

                    signals = self.strategy(self.store.get_data(current_tick))

                    if signals is None:
                        print("No Signal")
                        continue

                    with kafka_app.get_producer() as producer:
                        if isinstance(signals, Signal):
                            signals = [signals]

                        for signal in signals:
                            producer.produce(
                                topic=Topics.SIGNALS.value.name,
                                key=current_tick.encode("utf-8"),
                                value=json.dumps(
                                    SignalEvent(
                                        ticker=current_tick,
                                        strategy=self.config.name,
                                        quantity=signal.quantity,
                                        action=signal.action,
                                        type=signal.type,
                                        order_type=signal.order_type,
                                        sl=signal.sl,
                                        tp=signal.tp,
                                        limit_price=signal.limit_price,
                                        position=signal.position,
                                    ).model_dump()
                                ).encode("utf-8"),
                            )


if __name__ == "__main__":

    def strategyFn(data: pd.DataFrame):
        print("[S]: Strategy Runs")
        return [
            Signal(
                quantity=1,
                action="BUY",
                type="ENTRY",
                order_type="MARKET",
            )
        ]

    builder = StrategyBuilder(
        name="test",
        tickers="TATASTEEL.NSE",
        run_tf="1M",
        strategy=strategyFn,
        broker="UPSTOX",
    )
