from typing import Literal
from db import Database


class DataStore:
    def get_ticker(self, ticker: str):
        with Database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM tickers WHERE ticker = %s", (ticker,))
                data = cursor.fetchone()

                if data is None:
                    raise ValueError(f"Ticker {ticker} not found in database")

                return data

    def get_historic_data(
        self,
        ticker: str,
        freq: Literal["1M", "2M", "5M", "10M", "15M", "30M", "1H", "2H", "4H", "1D"],
        start_date: str | None = None,
        end_date: str | None = None,
    ):
        pass
