from db import Database
from fastapi import FastAPI
import pandas as pd
import uvicorn

app = FastAPI()
db = Database()


@app.get("/")
async def root():
    return {"status": "healthy"}


@app.get("/data/{ticker}")
async def main(ticker: str):
    query = """
        SELECT * FROM symbols
        WHERE query_key = $1;
    """
    conn = await db.get_connection()
    result = await conn.fetch(query, ticker)

    if result is None:
        return {
            "status": "error",
            "message": "Ticker not found",
        }

    query = """
        SELECT ts, open, high, low, close, volume
        FROM market_data 
        WHERE ticker = $1
        ORDER BY ts DESC;
    """

    result = await conn.fetch(query, ticker)
    df = pd.DataFrame(result, columns=["ts", "open", "high", "low", "close", "volume"])
    response = df.to_dict(orient="records")

    return response


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
    )
