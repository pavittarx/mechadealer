from datetime import date, datetime
from dotenv import load_dotenv

import pandas as pd
import requests
import gzip
import json

load_dotenv()

def transform_instruments(data, exchange: str):
    df = pd.DataFrame(data)
    df = df.rename(
        {
            "trading_symbol": "ticker",
            "underlying_symbol": "underlying_ticker",
            "qty_multiplier": "multiplier",
        },
        axis="columns",
    )

    df["active"] = True
    df["exchange"] = exchange
    df["market"] = "IN"
    df["source"] = "upstox"
    
    df["query_key"] = df["ticker"] + "." + df["exchange"]
    df["fetch_key"] = df["instrument_key"]
    df["segment"] = df["segment"].str.extract(r"_(.+)").fillna(df["segment"])
    df["priority"] = False

    df = df[
        [
            "query_key",
            "fetch_key",
            "source",
            "ticker",
            "tick_size",
            "name",
            "segment",
            "market",
            "exchange",
            "exchange_token",
            "lot_size",
            "multiplier",
            "priority",
            "active",
        ]
    ]
    
    default_values = {
        "multiplier": 0,
        "lot_size": 0,
        "tick_size": 0,
        "name": "",
        "segment": "",
        "exchange_token": 0,
    }

    df.fillna(default_values, inplace=True)

    return df

class UpstoxClient:
    def __init__(self):
        self.BASE_URL = "https://api-v2.upstox.com"
        
    def fetch_nse_instruments(self):
        url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
        response = requests.get(url)
        json_str = gzip.decompress(response.content)
        data = json.loads(json_str)
        df = transform_instruments(data, "NSE")
        return df
    
    def fetch_bse_instruments(self):
        url = "https://assets.upstox.com/market-quote/instruments/exchange/BSE.json.gz"
        response = requests.get(url)
        json_str = gzip.decompress(response.content)
        data = json.loads(json_str)
        df = transform_instruments(data,  "BSE")
        return df

    def fetch_historical_data(
        self,
        instrumentKey: str,
        toDate: date,
        fromDate: date | None = None,
    ):
        if not instrumentKey:
            raise Exception("Instrument Key is not provided")

        if not toDate:
            raise Exception("Start Date is not provided")

        if isinstance(toDate, datetime):
            toDate = toDate.date()

        url = self.BASE_URL

        if not fromDate:
            url += f"/historical-candle/{instrumentKey}/1minute/{toDate}"
        else:
            if isinstance(fromDate, datetime):
                fromDate = fromDate.date()

            url += f"/historical-candle/{instrumentKey}/1minute/{toDate}/{fromDate}"

        results = requests.get(url)
        data = results.json()
        if data["status"] == "success":
            data = data["data"]["candles"]
        else:
            print("[Error]", data)
            raise Exception("Failed to fetch data from Upstox API")

        df = pd.DataFrame(data)
        df.columns = [
            "ts",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "oi",
        ]

        return df

    def fetch_intraday_data(self, instrumentKey: str):
        if not instrumentKey:
            raise Exception("Instrument Key is not provided")

        url = self.BASE_URL
        url += f"/historical-candle/intraday/{instrumentKey}/1minute/"

        results = requests.get(url)
        data = results.json()
        if data["status"] == "success":
            data = data["data"]["candles"]
        else:
            print("[Error]", data)
            raise Exception("Failed to fetch data from Upstox API")

        df = pd.DataFrame(data)
        df.columns = [
            "ts",
            "open",
            "high",
            "low",
            "close",
            "volume",
            "oi",
        ]

        return df