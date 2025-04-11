import os
from dotenv import load_dotenv
import pandas as pd
from datetime import date, datetime
import requests

load_dotenv()


class UpstoxClient:
    def __init__(self):
        self.BASE_URL = "https://api-v2.upstox.com"
        # self.UPSTOX_API_KEY = config["UPSTOX_API_KEY"]
        # self.UPSTOX_API_SECRET = config["UPSTOX_API_SECRET"]

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


if __name__ == "__main__":
    client = UpstoxClient()
    client.fetch_intraday_data("NSE_EQ|INE081A01020")
