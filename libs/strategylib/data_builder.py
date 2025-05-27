import pandas as pd
from pandas import DataFrame
from typing import Dict


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
            df = df.set_index("ts")

            self.data[tick] = df

    def init_ticker_data(
        self,
        tick: str,
        df: DataFrame,
    ):
        if tick not in self.tickers:
            raise ValueError(f"Ticker {tick} not found in data store")

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
