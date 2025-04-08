from db import Database
from sources.upstox import UpstoxDataSource
import asyncio


async def main():
    await Database.init_database()
    print("Database initialized successfully!")


if __name__ == "__main__":
    asyncio.run(main())
