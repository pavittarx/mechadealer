from datetime import datetime
from typing import Literal

from .symbols import get_nse_instruments, get_bse_instruments
from .client import UpstoxClient


class UpstoxDataSource:
    def __init__(self, db):
        self.db = db
        self.client = UpstoxClient()

    async def __sync_nse_instruments(self):
        if not self.db:
            raise Exception("Database Instance is not available")

        df = get_nse_instruments()
        conn = await self.db.get_connection()

        try:
            now = datetime.now()
            query = "SELECT ticker FROM symbols WHERE exchange = 'NSE';"
            results = await conn.fetch(query)

            tickers = [row["ticker"] for row in results]
            df = df[~df["ticker"].isin(tickers)]

            records = df.to_records(index=False)
            values = [
                (
                    r.ticker,
                    r.tick_size,
                    r.name,
                    r.segment,
                    r.market,
                    r.exchange,
                    r.exchange_token,
                    r.instrument_key,
                    r.type,
                    r.lot_size or 0,
                    r.multiplier,
                    True if r.active else False,
                    now,
                    now,
                )
                for r in records
            ]

            if len(values) == 0:
                return

            query = """
                    INSERT INTO symbols 
                    (
                        query_key, fetch_key, source, tick_size, name, segment, market, exchange, exchange_token,
                        instrument_key, type, lot_size, multiplier, active, updated_at, created_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14);
                """

            for row in values:
                await conn.execute(query, *row)

        finally:
            await self.db.release_connection(conn)

    async def __sync_bse_instruments(self):
        if not self.db:
            raise Exception("Database Instance is not available")

        df = get_bse_instruments()
        conn = await self.db.get_connection()

        try:
            now = datetime.now()
            query = "SELECT ticker FROM symbols WHERE exchange = 'NSE';"
            results = await conn.fetch(query)

            tickers = [row["ticker"] for row in results]
            df = df[~df["ticker"].isin(tickers)]

            records = df.to_records(index=False)
            values = [
                (
                    r.ticker,
                    r.tick_size,
                    r.name,
                    r.segment,
                    r.market,
                    r.exchange,
                    r.exchange_token,
                    r.instrument_key,
                    r.type,
                    r.lot_size or 0,
                    r.multiplier,
                    True if r.active else False,
                    now,
                    now,
                )
                for r in records
            ]

            if len(values) == 0:
                return

            query = """
                    INSERT INTO symbols 
                    (
                        ticker, tick_size, name, segment, market, exchange, exchange_token,
                        instrument_key, type, lot_size, multiplier, active, updated_at, created_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14);
                """

            for row in values:
                await conn.execute(query, *row)

        finally:
            await self.db.release_connection(conn)

    async def fetch_instruments(self):
        await self.__sync_nse_instruments()
        await self.__sync_bse_instruments()

    async def get_data(
        self,
        ticker: str,
        interval: Literal["1M", "2M", "5M", "15M", "30M", "1H", "4H", "D"],
        end_date: datetime,
        start_date: datetime | None = None,
    ):
        ticker, exchange = ticker.split(".")

        conn = await self.db.get_connection()
        query = (
            f"SELECT * from symbols WHERE ticker='{ticker}' and exchange='{exchange}';"
        )

        result = await conn.fetch(query)

        if result is None:
            raise Exception(f"Provided ticker {ticker} does not exist.")
        else:
            result = dict(result[0])

        df = self.client.fetch_historical_data(
            result["instrument_key"], end_date, start_date
        )

        return df
