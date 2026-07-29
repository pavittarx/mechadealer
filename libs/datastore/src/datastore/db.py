import os
from contextlib import contextmanager

import psycopg_pool

SYMBOLS_DDL = """
    CREATE TABLE IF NOT EXISTS symbols (
        query_key STRING,
        fetch_key STRING,
        source SYMBOL,
        ticker STRING,
        tick_size DOUBLE,
        name STRING,
        segment SYMBOL,
        market SYMBOL,
        exchange SYMBOL,
        exchange_token STRING,
        lot_size FLOAT,
        multiplier DOUBLE,
        active BOOLEAN,
        priority BOOLEAN,
        updated_at TIMESTAMP,
        created_at TIMESTAMP
    );
"""

# High cardinality. `oi` is written by datasync and read back by
# DataStore.get_historic_data, so it has to be declared here -- relying on
# QuestDB to add it on first ingest left the column missing until then.
MARKET_DATA_DDL = """
    CREATE TABLE IF NOT EXISTS market_data (
        ticker SYMBOL,
        ts TIMESTAMP,
        open DOUBLE,
        high DOUBLE,
        low DOUBLE,
        close DOUBLE,
        volume LONG,
        oi DOUBLE
    )
    timestamp(ts)
    PARTITION BY DAY WAL
    DEDUP UPSERT KEYS(ts, ticker);
"""


class Database:
    _pool = None

    def __init__(self, init_schema: bool = True):
        if init_schema:
            self.init_schema()

    @classmethod
    def init_schema(cls):
        """Create the QuestDB tables if they are missing."""
        with cls.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(SYMBOLS_DDL)
            cursor.execute(MARKET_DATA_DDL)

    @classmethod
    def get_pool(cls):
        if cls._pool is None:
            qdb_conn_str = os.getenv("QDB_CONNECTION_STRING")

            if qdb_conn_str is None:
                raise RuntimeError(
                    "QDB_CONNECTION_STRING not set in environment variables"
                )

            cls._pool = psycopg_pool.ConnectionPool(
                conninfo=qdb_conn_str,
                min_size=5,
                max_size=20,
                kwargs={"autocommit": True},
            )

        return cls._pool

    @classmethod
    @contextmanager
    def get_connection(cls):
        pool = cls.get_pool()
        conn = pool.getconn()
        try:
            yield conn
        finally:
            pool.putconn(conn)

    @classmethod
    def release_connection(cls, conn):
        cls.get_pool().putconn(conn)

    @classmethod
    def reset_pool(cls):
        """Drop the cached pool. Used by tests."""
        if cls._pool is not None:
            cls._pool.close()
        cls._pool = None
