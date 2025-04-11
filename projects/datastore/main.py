from db import Database
from sources.upstox import UpstoxDataSource
from datetime import datetime
import asyncio


async def main():
    await Database.init_database()
    upstox = UpstoxDataSource(Database)
    # await upstox.fetch_instruments()
    await upstox.fetch_data(
        ticker="TATASTEEL",
        interval="1M",
        end_date=datetime.now(),
    )


if __name__ == "__main__":
    asyncio.run(main())
