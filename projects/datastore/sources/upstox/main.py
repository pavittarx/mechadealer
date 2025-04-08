import os
import dotenv
import asyncio
import pandas as pd

import upstox_client as upstox
# from upstox_client.rest import ApiException

from .symbols import get_nse_instruments, get_bse_instruments

dotenv.load_dotenv()
config = upstox.Configuration(sandbox=True)
config.access_token = os.getenv("UPSTOX_ACCESS_TOKEN") or ""


class UpstoxDataSource:
    def __init__(self, db):
        self.db = self.db

    async def fetch_instruments(self):
        if not self.db:
            raise Exception("Database Instance is not available")

    def fetch_data(self, symbol, interval, start_date, end_date):
        pass
