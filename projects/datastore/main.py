import uvicorn
from db import Database
from sources.upstox import UpstoxDataSource
from datetime import datetime
from fastapi import FastAPI
import asyncio

app = FastAPI()


@app.get("/")
async def root():
    return {"status": "healthy"}


@app.get("/data")
async def main():
    upstox = UpstoxDataSource(Database)

    ticker = "TATASTEEL.NSE"
    _, exchange = ticker.split(".")

    supported_exchanges = ["NSE", "BSE"]
    if exchange not in supported_exchanges:
        raise Exception(f"{exchange} Exchange is not currently supported.")

    if exchange == "NSE" or exchange == "BSE":
        result = await upstox.get_data(
            ticker=ticker,
            interval="1M",
            end_date=datetime.now(),
        )

        if result is None:
            raise Exception(f"Provided ticker {ticker} does not exist.")

        else:
            return {"status": "success", "data": result.to_dict(orient="records")}

    return True


@app.get("/sync")
async def sync():
    await Database.init_database()
    upstox = UpstoxDataSource(Database)
    await upstox.fetch_instruments()
    
    return {"status": "success"}


if __name__ == "__main__":
    # config = uvicorn.Config("main:app", port=5000, log_level="info")
    # server = uvicorn.Server(config)
    # server.run()
    
    asyncio.run(sync())