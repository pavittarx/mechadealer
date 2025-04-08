import asyncpg
import os
from dotenv import load_dotenv
from questdb.ingress import Sender

load_dotenv()


class Database:
    _pool = None
    _sender = None

    @classmethod
    async def init_database(cls):
        conn = await cls.get_connection()

        # Symbols table (low cardinality)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS symbols (
                ticker SYMBOL,
                tick_size DOUBLE,
                name SYMBOL,
                segment SYMBOL,
                market SYMBOL,
                exchange SYMBOL,
                exchange_token SYMBOL,
                instrument_key SYMBOL,
                type SYMBOL,
                lot_size LONG,
                multiplier DOUBLE,
                active BOOLEAN,
                updated_at TIMESTAMP,
                created_at TIMESTAMP
            );
        """)

        # Market data table (high cardinality)
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                ticker SYMBOL,
                timestamp TIMESTAMP,
                open DOUBLE,
                high DOUBLE,
                low DOUBLE,
                close DOUBLE,
                volume LONG
                ) timestamp(timestamp) 
            PARTITION BY DAY;
        """)

        await conn.close()

        return True

    @classmethod
    async def get_pool(cls):
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
    async def get_sender(cls):
        if cls._sender is None:
            cls._sender = await Sender.from_conf(os.getenv("QDB_CLIENT_CONF"))
        return cls._sender

    @classmethod
    async def release_connection(cls, connection):
        pool = await cls.get_pool()
        await pool.release(connection)
