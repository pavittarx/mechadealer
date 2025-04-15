from questdb.ingress import Sender
from contextlib import contextmanager
import psycopg
import psycopg_pool
import os



qdb_conn_str = os.getenv("QDB_CONNECTION_STRING")
qdb_conf = os.getenv("QDB_CLIENT_CONF")

if qdb_conn_str is None:
    raise ValueError("QDB_CONNECTION_STRING not set in environment variables")

if qdb_conf is None:
    raise ValueError("QUEST_CLIENT_CONF not set in environment variables")

class Database:
    _pool = None
    _sender = None

    @classmethod
    def __init__(cls):
        if qdb_conn_str is None:
            raise ValueError("QDB_CONNECTION_STRING not set in environment variables")
        
        if cls._pool is None: 
            cls._pool = psycopg_pool.ConnectionPool(
                conninfo=qdb_conn_str, 
                min_size=5,
                max_size=20,
                kwargs={"autocommit":True},
            )

        conn = cls._pool.getconn()
        try:
            cursor = conn.cursor()
            cursor.execute("""
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
            """)

            # Market data table (high cardinality)
            cursor.execute("""
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
        finally:
            cls._pool.putconn(conn)

    @classmethod
    def get_pool(cls):
        if qdb_conn_str is None:
            raise ValueError("QDB_CONNECTION_STRING not set in environment variables")

        if cls._pool is None: 
            cls._pool = psycopg_pool.ConnectionPool(
                conninfo=qdb_conn_str, 
                min_size=5,
                max_size=20,
                kwargs={"autocommit":True},
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
    @contextmanager
    def get_sender(cls):
        return Sender.from_env()

    @classmethod
    def release_connection(cls, conn):
        pool = cls.get_pool()
        
        if pool is None:
            raise ValueError("Connection pool not initialized")
        
        pool.putconn(conn)