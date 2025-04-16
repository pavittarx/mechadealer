import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    _pool = None
    _sender = None
    _init = False
        
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
    async def release_connection(cls, connection):
        pool = await cls.get_pool()
        await pool.release(connection)
