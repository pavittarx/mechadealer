
from prefect import flow, task
from dotenv import load_dotenv
from datetime import datetime

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
                 'fetch_key': tick[1]
                 } for tick in tickers ]
    
    return tickers

@task
def get_non_priority_tickers_list():
    query = """
                SELECT DISTINCT query_key, fetch_key, priority,
                FROM symbols
                WHERE priority = FALSE;
            """
        
    cursor = conn.cursor()
    cursor.execute(query)
    tickers = cursor.fetchall() 
    
    tickers  = [{'query_key': tick[0], 
                 'fetch_key': tick[1]
                 } for tick in tickers ]
    
    return tickers

@task 
def latest_data_timestamp(ticker):
    query = """
                SELECT ts, ticker 
                FROM market_data  1
                WHERE ticker = %s 
                ORDER BY ts DESC;
            """
        
    cursor = conn.cursor()
    cursor.execute(query, (ticker["query_key"],))
    
    data = cursor.fetchone()
    
    if data is None:
        return None
    else:
        return data[0]

@task
def fetch_data_historic(ticker: dict, latest_ts: datetime | None =None):
    client = UpstoxClient()
    
    if latest_ts is None:
        candles = client.fetch_historical_data(
            ticker["fetch_key"],
            datetime.now(),
        )
        
    else:
        candles = client.fetch_historical_data(
            ticker["fetch_key"],
            datetime.now(),
            latest_ts
        )
        
    return candles
    
    
@task
def fetch_data_intraday(ticker: dict):
    client = UpstoxClient()
    
    candles = client.fetch_intraday_data(
            ticker["fetch_key"],
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
def fetch_and_save(tick: dict): 
    latest_ts: datetime | None = latest_data_timestamp(tick)
        
    # Fetch historic data if no data or data is old 
    if latest_ts is None:
        data = fetch_data_historic(tick)
        save_data(tick, data)
            
    else:      
        today = datetime.now().date()
        latest_date = latest_ts.date()
        
        if latest_date < today:
            data = fetch_data_historic(tick, latest_ts)
            save_data(tick, data)
            
    # Fetch Intraday data
    data = fetch_data_intraday(tick)
    save_data(tick, data) 

@flow
def fetch_priority_tickers():
    tickers = get_priority_tickers_list()
    for tick in tickers:
        fetch_and_save(tick)
        
@flow 
def fetch_non_priority_tickers():
    tickers = get_non_priority_tickers_list()
    for tick in tickers:
        fetch_and_save(tick)