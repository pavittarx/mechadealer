import asyncpg
import os
from dotenv import load_dotenv
from questdb.ingress import Sender

load_dotenv()

class Database:
    _pool = None
    _sender = None
    _init = False

    @classmethod
    def check_init(cls):
        if not cls._init:
            raise Exception("Database not initialized")

    @classmethod
    async def init_database(cls):
        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                os.getenv("QDB_CONNECTION_STRING"), min_size=5, max_size=20
            )

        conn = await cls._pool.acquire()

        try:
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS symbols (
                    query_key STRING,
                    fetch_key STRING,
                    source SYMBOL,
                    tick_size DOUBLE,
                    name STRING,
                    segment SYMBOL,
                    market SYMBOL,
                    exchange SYMBOL,
                    exchange_token STRING,
                    instrument_key STRING,
                    type SYMBOL,
                    lot_size FLOAT,
                    multiplier DOUBLE,
                    active BOOLEAN,
                    priority BOOLEAN,
                    updated_at TIMESTAMP,
                    created_at TIMESTAMP
                );
            """)

            # Market data table (high cardinality)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS market_data (
                    ticker SYMBOL,
                    ts TIMESTAMP,
                    open DOUBLE,
                    high DOUBLE,
                    low DOUBLE,
                    close DOUBLE,
                    volume LONG
                ) 
                timestamp(ts) 
                PARTITION BY DAY WAL
                DEDUP UPSERT KEYS(ts, ticker);
            """)

            cls._init = True
        finally:
            await cls._pool.release(conn)

    @classmethod
    async def get_pool(cls):
        cls.check_init()

        if cls._pool is None:
            cls._pool = await asyncpg.create_pool(
                os.getenv("QDB_CONNECTION_STRING"), min_size=5, max_size=20
            )
        return cls._pool

    @classmethod
    async def get_connection(cls):
        pool = await cls.get_pool()
        return await pool.acquire()

    @classmethod
    def get_sender(cls):
        if cls._sender is None:
            cls._sender = Sender.from_conf(os.getenv("QDB_CLIENT_CONF"))
        return cls._sender

    @classmethod
    async def release_connection(cls, connection):
        pool = await cls.get_pool()
        await pool.release(connection)
