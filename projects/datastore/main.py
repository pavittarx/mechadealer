from db import Database
from fastapi import FastAPI
import asyncio

app = FastAPI()
db = Database()

@app.get("/")
async def root():
    return {"status": "healthy"}


# @app.get("/data/{ticker}")
async def main(ticker: str):
    query = """
        SELECT * FROM symbols
        WHERE query_key = $1;
    """
    conn = await db.get_connection()
    result = await conn.fetch(query, ticker)
    
    print(f"Query result for {ticker}: {result}")
    

if __name__ == "__main__":
    asyncio.run(main("TATASTEEL.NSE"))