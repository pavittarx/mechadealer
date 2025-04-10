import requests
import os
import gzip
import json
import dotenv
import asyncio
import pandas as pd

import upstox_client as upstox

# from upstox_client.rest import ApiException
from db import Database
from datetime import datetime

dotenv.load_dotenv()
config = upstox.Configuration(sandbox=True)
config.access_token = os.getenv("UPSTOX_ACCESS_TOKEN") or ""


def get_nse_instruments():
    url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
    response = requests.get(url)
    json_str = gzip.decompress(response.content)
    data = json.loads(json_str)
    return data


def get_bse_instruments():
    url = "https://assets.upstox.com/market-quote/instruments/exchange/BSE.json.gz"
    response = requests.get(url)
    json_str = gzip.decompress(response.content)
    data = json.loads(json_str)
    return data


class UpstoxDataSource:
    def __init__(self):
        pass

    async def fetch_instruments(self):
        nse = get_nse_instruments()

        print("NSE instruments fetched")
        df = pd.DataFrame(nse)
        df = df.rename(
            {
                "trading_symbol": "ticker",
                "underlying_symbol": "underlying_ticker",
                "qty_multiplier": "multiplier",
            },
            axis="columns",
        )

        df = df[
            [
                "ticker",
                "tick_size",
                "name",
                "segment",
                "exchange_token",
                "instrument_key",
                # "type",
                "lot_size",
                "multiplier",
                # "active",
            ]
        ]

        df["exchange"] = "NSE"
        df["market"] = "IN"
        df["updated_at"] = datetime.now()

        print(df)

    def fetch_data(self, symbol, interval, start_date, end_date):
        pass


if __name__ == "__main__":
    upstoxDS = UpstoxDataSource()
    asyncio.run(upstoxDS.fetch_instruments())
