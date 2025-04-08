import requests
import gzip
import json
import pandas as pd
from datetime import datetime


def format_instruments(data):
    df = pd.DataFrame(data)
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

    return df


def get_nse_instruments():
    url = "https://assets.upstox.com/market-quote/instruments/exchange/NSE.json.gz"
    response = requests.get(url)
    json_str = gzip.decompress(response.content)
    data = json.loads(json_str)
    df = format_instruments(data)
    return df


def get_bse_instruments():
    url = "https://assets.upstox.com/market-quote/instruments/exchange/BSE.json.gz"
    response = requests.get(url)
    json_str = gzip.decompress(response.content)
    data = json.loads(json_str)
    df = format_instruments(data)
    return df
