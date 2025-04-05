import asyncio
from db import Database


async def init_database():
    conn = await Database.get_connection()

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


if __name__ == "__main__":
    asyncio.run(init_database())
