
from httpx import get
from prefect import flow, task
from dotenv import load_dotenv
from datetime import date, datetime

from questdb.ingress import Sender
from sources.upstox import UpstoxClient

import pandas as pd
import psycopg as pg
import os

load_dotenv()

qdb_conn_str = os.getenv("QDB_CONNECTION_STRING")
qdb_conf = os.getenv("QDB_CLIENT_CONF")

if qdb_conn_str is None:
    raise ValueError("QDB_CONNECTION_STRING not set in environment variables")

if qdb_conf is None:
    raise ValueError("QUEST_CLIENT_CONF not set in environment variables")

conn = pg.connect(qdb_conn_str, autocommit=True)

@task
def get_priority_tickers_list():
    query = """
                SELECT DISTINCT query_key, fetch_key, priority,
                FROM symbols
                WHERE priority = TRUE;
            """
        
    cursor = conn.cursor()
    cursor.execute(query)
    tickers = cursor.fetchall() 
    
    tickers  = [{'query_key': tick[0], 
                 'fetch_key': tick[1],
                 'priority': False
                 } for tick in tickers ]
    
    return tickers

@task
def fetch_data(ticker):
    client = UpstoxClient()
    
    query = """
        SELECT * 
        FROM market_data
        LATEST ON ts
        PARTITION BY ts;
    """
    
    cursor = conn.cursor()
    cursor.execute(query)
    
    data = cursor.fetchone()
    
    candles = None
    
    if data is None:
        candles = client.fetch_historical_data(
            ticker["fetch_key"],
            datetime.now(),
        )
        
    else:
        candles = client.fetch_historical_data(
            ticker["fetch_key"],
            datetime.now(),
            # datetime(data[0]),
        )
        
    return candles
    

@task
def save_data(ticker, data):
    print('Saving Data', ticker, data)
    
    df = pd.DataFrame(data, columns=['ts', 'open', 'high', 'low', 'close', 'volume', 'oi'])
    df['ticker'] = ticker['query_key']
    df['ts'] = pd.to_datetime(df['ts'])
    
    with Sender.from_env() as sender:
        sender.dataframe(
            df=df,
            table_name="market_data",
            symbols=['ticker'],
            at="ts",
        )
        
    print('Data Ingested for Ticker', ticker['query_key'])
    

@task
def get_all_tickers():
    return []

@flow
def fetch_priority_tickers():
    tickers = get_priority_tickers_list()
    for tick in tickers:
        data = fetch_data(tick)
        save_data(tick, data)

@flow
def fetch_all_tickers():
    tickers = get_all_tickers()
    for tick in tickers:
        data = fetch_data(tick)
        save_data(tick, data)
        
        
if __name__ == "__main__":
    tickers = get_priority_tickers_list()
    for tick in tickers:
        data = fetch_data(tick)
        save_data(tick, data)
    # fetch_priority_tickers()
    # fetch_all_tickers()