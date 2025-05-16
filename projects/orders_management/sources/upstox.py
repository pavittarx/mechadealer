from typing import Literal
import requests
import os

from dotenv import load_dotenv
from datastore import DataStore

ds = DataStore()

load_dotenv()
BASE_URL = "https://api.upstox.com"
BASE_URL_SANDBOX = "https://api-sandbox.upstox.com"
BASE_URL_LIVE = "https://api-hft.upstox.com"

client_id = os.getenv("UPSTOX_CLIENT_ID")
client_secret = os.getenv("UPSTOX_CLIENT_SECRET")

if not client_id:
    raise ValueError("UPSTOX_CLIENT_ID is not set in the environment variables.")

if not client_secret:
    raise ValueError("UPSTOX_CLIENT_SECRET is not set in the environment variables.")


class UpstoxBroker:
    def __init__(self, strategy: str):
        if not strategy:
            raise ValueError("Strategy Name must be provided.")

        self.strategy = strategy
        self.token = self.get_token()

    def _get_headers(self):
        return {
            "Accept": "application/json",
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def get_token(self, live: bool = False):
        # TODO: to be implemented with live app.
        # sandbox token provided below
        # if not live:
        #     return "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzSEM1WjIiLCJqdGkiOiI2ODI1NTVkNjdmZWVjZjQ1YTEzNWI5MmEiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6dHJ1ZSwiaWF0IjoxNzQ3Mjc3MjcwLCJpc3MiOiJ1ZGFwaS1nYXRld2F5LXNlcnZpY2UiLCJleHAiOjE3NDk4NTIwMDB9.j6QlJokP-yyxNSqMUcJPUFryUyeMKbJNKTGAUMM62mQ"

        return "eyJ0eXAiOiJKV1QiLCJrZXlfaWQiOiJza192MS4wIiwiYWxnIjoiSFMyNTYifQ.eyJzdWIiOiIzSEM1WjIiLCJqdGkiOiI2ODI1NGVjZWZlMDgyYTU0NDEzYTU0NDQiLCJpc011bHRpQ2xpZW50IjpmYWxzZSwiaXNQbHVzUGxhbiI6ZmFsc2UsImlhdCI6MTc0NzI3NTQ3MCwiaXNzIjoidWRhcGktZ2F0ZXdheS1zZXJ2aWNlIiwiZXhwIjoxNzQ3MzQ2NDAwfQ.Ywa0hGUu_HEhMXOkKyuv0KtgHgDdxr-1T_S5yrddkXA"

    def fetch_account_balance(self):
        try:
            url_fund_and_margin = f"{BASE_URL}/v2/user/get-funds-and-margin"
            headers = self._get_headers()

            res_fund_and_margin = requests.get(url_fund_and_margin, headers=headers)
            res_fund_and_margin.raise_for_status()

            data = res_fund_and_margin.json()["data"]

            return data["equity"]

        except Exception as e:
            print("Error fetching account balance:", e)
            return None

    def order_send(
        self,
        ticker: str,
        action: Literal["BUY", "SELL"],
        quantity: float,
        order_type: Literal["LIMIT", "MARKET"],
        price: float | None = None,
    ):
        try:
            ticker = ds.get_ticker(ticker)

            if not ticker:
                print("Ticker not found in the datastore.")
                return

            instrument_token = ticker[1]

            url = f"{BASE_URL_LIVE}/v3/order/place"
            payload = {
                "instrument_token": instrument_token,
                "quantity": quantity,
                "order_type": order_type,
                "transaction_type": action,
                "tag": self.strategy,
                "product": "D",
                "validity": "DAY",
                "price": 0 if order_type == "MARKET" else price,
                "disclosed_quantity": 0,
                "trigger_price": 0,
                "is_amo": False,
                "slice": False,
            }

            headers = self._get_headers()

            res = requests.post(url, json=payload, headers=headers)
            res.raise_for_status()

            data = res.json()["data"]
            orders: list[str] = data["order_ids"] or []

            return orders

        except Exception as e:
            print("Error sending order:", e)
            raise

    def order_get(self, order_id: str):
        if not order_id:
            print("Order ID is required.")
            return

        try:
            url = f"{BASE_URL}/v2/order/details"
            headers = self._get_headers()
            url += f"?order_id={order_id}"
            res = requests.get(url, headers=headers)
            res.raise_for_status()
            data = res.json()["data"]

            return data

        except Exception as e:
            print("Error fetching order status:", e)
            raise

    def fetch_positions(self):
        try:
            url = f"{BASE_URL}/v2/portfolio/short-term-positions"
            headers = self._get_headers()

            res = requests.get(url=url, headers=headers)
            res.raise_for_status()

            res = res.json()
            data = res["data"]

            print(data)
            return data

        except Exception as e:
            print("Error while fetching positions", e)
            raise

    def fetch_trades_today(self):
        try:
            url = f"{BASE_URL}/v2/order/trades/get-trades-for-day"
            headers = self._get_headers()

            res = requests.get(url=url, headers=headers)
            res.raise_for_status()
            data = res.json()["data"]
            return data
        except Exception as e:
            print("Error while fetching trades", e)
            raise

    def fetch_orders_today(self):
        try:
            url = f"{BASE_URL}/v2/order/history"
            headers = self._get_headers()

            res = requests.get(url=url, headers=headers)
            res.raise_for_status()
            data = res.json()["data"]
            return data

        except Exception as e:
            print("Error while fetching orders", e)
            raise
