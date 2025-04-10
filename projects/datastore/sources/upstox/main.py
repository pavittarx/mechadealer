import os
import dotenv

from datetime import datetime
import upstox_client as upstox
import numpy as np
# from upstox_client.rest import ApiException

from .symbols import get_nse_instruments, get_bse_instruments

dotenv.load_dotenv()
config = upstox.Configuration(sandbox=True)
config.access_token = os.getenv("UPSTOX_ACCESS_TOKEN") or ""


class UpstoxDataSource:
    def __init__(self, db):
        self.db = db

    async def __fetch_nse_instruments(self):
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
                        ticker, tick_size, name, segment, market, exchange, exchange_token,
                        instrument_key, type, lot_size, multiplier, active, updated_at, created_at
                    )
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14);
                """

            for row in values:
                await conn.execute(query, *row)

        finally:
            await self.db.release_connection(conn)

    async def __fetch_bse_instruments(self):
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
        await self.__fetch_nse_instruments()
        await self.__fetch_bse_instruments()

    async def fetch_data(self, symbol, interval, start_date, end_date):
        pass
