import pytz
import pandas as pd
from typing import Literal
from db import Database
from datetime import timezone

freq_map = {
    "1M": "1T",  # 1 minute
    "2M": "2T",  # 2 minutes
    "5M": "5T",  # 5 minutes
    "10M": "10T",  # 10 minutes
    "15M": "15T",  # 15 minutes
    "30M": "30T",  # 30 minutes
    "1H": "1H",  # 1 hour
    "2H": "2H",  # 2 hours
    "4H": "4H",  # 4 hours
    "1D": "1D",  # 1 day
}


class DataStore:
    def get_ticker(self, ticker: str):
        with Database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT * FROM symbols WHERE query_key = %s", (ticker,))
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
        tz: str = "Asia/Kolkata",
    ):
        query_chunks = ["SELECT * FROM market_data WHERE ticker = %s"]
        params = [ticker]

        if start_date:
            query_chunks.append("AND ts >= %s")
            params.append(start_date)

        if end_date:
            query_chunks.append("AND ts <= %s")
            params.append(end_date)

        query_chunks.append("ORDER BY ts;")
        query = " ".join(query_chunks)
        print(query, params)

        with Database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)  # type: ignore
                data = cursor.fetchall()

                if data is None:
                    raise ValueError(f"No data found for ticker {ticker}")

                df = pd.DataFrame(
                    data,
                    columns=[
                        "ticker",
                        "ts",
                        "open",
                        "high",
                        "low",
                        "close",
                        "volume",
                        "oi",
                    ],
                )

                df["ts"] = pd.to_datetime(df["ts"], utc=True).dt.tz_convert(tz)
                df.set_index("ts", inplace=True)

                if freq != "1M":
                    if freq not in freq_map.keys():
                        raise ValueError(f"Invalid frequency: {freq}")

                    df = df.resample(freq_map[freq]).agg(
                        {
                            "open": "first",
                            "high": "max",
                            "low": "min",
                            "close": "last",
                            "volume": "sum",
                            "oi": "last",
                        }
                    )
                    df.dropna(inplace=True)

                return df

    def add_to_priority(self, ticker: str):
        if ticker is None:
            raise ValueError("Ticker cannot be None")

        result = self.get_ticker(ticker)

        if result is None:
            raise ValueError(f"Ticker {ticker} is not available")

        with Database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE symbols SET priority = TRUE WHERE query_key = %s", (ticker,)
                )

                if cursor.rowcount == 0:
                    raise ValueError(f"Failed to update priority for ticker {ticker}")

                conn.commit()

    def remove_from_priority(self, ticker: str):
        if ticker is None:
            raise ValueError("Please provide the ticker")

        result = self.get_ticker(ticker)

        if result is None:
            raise ValueError(f"Ticker {ticker} is not available")

        with Database.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "UPDATE symbols SET priority = FALSE WHERE query_key = %s",
                    (ticker,),
                )

                if cursor.rowcount == 0:
                    raise ValueError(f"Failed to update priority for ticker {ticker}")

                conn.commit()


if __name__ == "__main__":
    ds = DataStore()
    # print(ds.get_ticker("TATASTEEL.NSE"))
    # print(ds.get_historic_data("TATASTEEL.NSE", "1M"))
    print(ds.add_to_priority("TATASTEEL.NSE"))
