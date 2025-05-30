import pytz
import json
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from questdb.ingress import Sender
from prefect import flow, task
from prefect.schedules import RRule

from sources.upstox import UpstoxClient
from datastore import Database, DataStore
from kafkalib import Kafka, Topics

load_dotenv()
db = Database()
ds = DataStore()
client = UpstoxClient()

local_tz = pytz.timezone("Asia/Kolkata")

tf_multiplier = {
    "1M": 1,
    "2M": 2,
    "3M": 3,
    "5M": 5,
    "10M": 10,
    "15M": 15,
    "30M": 30,
    "1H": 60,
    "4H": 240,
}

resample_freq = {
    "1M": "1T",
    "2M": "2T",
    "3M": "3T",
    "5M": "5T",
    "10M": "10T",
    "15M": "15T",
    "30M": "30T",
    "1H": "1H",
    "4H": "4H",
    "1D": "1D",
}


@task
def get_priority_tickers_list():
    query = """
                SELECT DISTINCT query_key, fetch_key, priority,
                FROM symbols
                WHERE priority = TRUE;
            """

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        tickers = cursor.fetchall()

        tickers = [{"query_key": tick[0], "fetch_key": tick[1]} for tick in tickers]
        return tickers


@task
def get_non_priority_tickers_list():
    query = """
                SELECT DISTINCT query_key, fetch_key, priority,
                FROM symbols
                WHERE priority = FALSE;
            """

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query)
        tickers = cursor.fetchall()

        tickers = [{"query_key": tick[0], "fetch_key": tick[1]} for tick in tickers]

        return tickers


@task
def latest_data_timestamp(ticker):
    query = """
                SELECT ts, ticker 
                FROM market_data  1
                WHERE ticker = %s 
                ORDER BY ts DESC;
            """

    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(query, (ticker["query_key"],))

        data = cursor.fetchone()

        if data is None:
            return None
        else:
            return data[0]


@task
def fetch_data_historic(ticker: dict[str, str], latest_ts: datetime | None = None):
    if latest_ts is None:
        candles = client.fetch_historical_data(
            ticker["fetch_key"],
            datetime.now(),
        )

    else:
        candles = client.fetch_historical_data(
            ticker["fetch_key"], datetime.now(), latest_ts
        )

    return candles


@task
def fetch_data_intraday(ticker: dict[str, str]):
    candles = client.fetch_intraday_data(
        ticker["fetch_key"],
    )

    return candles


@task
def save_data(ticker, data):
    df = pd.DataFrame(
        data, columns=["ts", "open", "high", "low", "close", "volume", "oi"]
    )
    df["ticker"] = ticker["query_key"]
    df["ts"] = pd.to_datetime(df["ts"])

    with Sender.from_env() as sender:
        sender.dataframe(
            df=df,
            table_name="market_data",
            symbols=["ticker"],
            at="ts",
        )

    print("Data Ingested for Ticker", ticker["query_key"])


@task
def fetch_data(tick: dict[str, str]):
    latest_ts: datetime | None = latest_data_timestamp(tick)

    data = None

    # Fetch historic data if no data or data is old
    if latest_ts is None:
        data = fetch_data_historic(tick)

    else:
        today = datetime.now().date()
        latest_date = latest_ts.date()

        if latest_date < today:
            data = fetch_data_historic(tick, latest_ts)

    # Fetch Intraday data
    if data is None:
        data = fetch_data_intraday(tick)
        return data
    else:
        current_data = fetch_data_intraday(tick)
        data = pd.concat([data, current_data], ignore_index=True)
        return data


@task
def sync_instruments():
    nse = client.fetch_nse_instruments()
    bse = client.fetch_bse_instruments()

    df = pd.concat([nse, bse], ignore_index=True)
    now = datetime.now().isoformat()
    df["updated_at"] = now
    df["created_at"] = now

    existing_keys = set()
    with db.get_connection() as conn:
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT query_key FROM symbols")
            existing_keys = {row[0] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error fetching existing keys: {e}")

        # Filter out existing records
    df = df[~df["query_key"].isin(existing_keys)]

    if df.empty:
        print("No new instruments to add")
        return 0

    # Insert new records in batches
    batch_size = 1000
    inserted_count = 0

    with db.get_connection() as conn:
        cursor = conn.cursor()

        # Prepare the insert query with placeholders
        query = """
            INSERT INTO symbols (
                query_key, fetch_key, source, ticker, tick_size,
                name, segment, market, exchange, exchange_token,
                lot_size, multiplier, priority, active,
                updated_at, created_at
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s
            )
        """

        values = [
            tuple(row)
            for row in df[
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
                    "updated_at",
                    "created_at",
                ]
            ].to_records(index=False)
        ]

        # Insert in batches
        for i in range(0, len(values), batch_size):
            batch = values[i : i + batch_size]
            try:
                cursor.executemany(query, batch)
                inserted_count += len(batch)
                print(
                    f"Inserted batch {i // batch_size + 1}/{(len(values) + batch_size - 1) // batch_size}"
                )
            except Exception as e:
                print(f"Error inserting batch: {e}")

    print(f"Successfully added {inserted_count} new instruments")
    return inserted_count


@task
def trigger_kafka_events(tick: dict[str, str], data):
    k = Kafka()
    app = k.get_app()

    feed_1M = app.topic(name=Topics.FEED_1M.value.name, value_serializer="json")
    row = data.iloc[0]

    message = {
        "ticker": tick["query_key"],
        "ts": row["ts"],
        "open": float(row["open"]),
        "high": float(row["high"]),
        "low": float(row["low"]),
        "close": float(row["close"]),
        "volume": int(row["volume"]),
        "oi": float(row["oi"]),
    }

    with app.get_producer() as producer:
        kafka_msg = feed_1M.serialize(key=message["ticker"], value=message)

        producer.produce(
            topic=feed_1M.name,
            key=kafka_msg.key,
            value=kafka_msg.value,
        )

        message["ts"] = datetime.fromisoformat(message["ts"]).astimezone(local_tz)
        data_1M = ds.get_historic_data(
            ticker=message["ticker"],
            freq="1M",
        )

        if data_1M is not None:
            df = pd.DataFrame([message])
            df.set_index("ts", inplace=True)
            data_1M = pd.concat([data_1M, df])
            data_1M = data_1M.sort_index()

            timeframe = ["2M", "3M", "5M", "10M", "15M", "30M", "1H", "4H"]
            now = datetime.now()
            start_of_market = now.replace(hour=9, minute=15, second=0, microsecond=0)
            time_diff = (now - start_of_market).total_seconds() / 60

            for tf in timeframe:
                if int(time_diff % tf_multiplier[tf]) == 0:
                    topic = Topics["FEED_" + tf].value
                    freq = resample_freq[tf]
                    data_tf = data_1M.resample(freq).agg(
                        {
                            "open": "first",
                            "high": "max",
                            "low": "min",
                            "close": "last",
                            "volume": "sum",
                            "oi": "last",
                        }
                    )

                    row = data_tf.iloc[-1]

                    print("IDX", tf, data_tf.tail(5))

                    ts = (
                        row.name
                        if isinstance(row.name, pd.Timestamp)
                        else pd.Timestamp(row.name)
                    )

                    message_tf = {
                        "ticker": tick,
                        "ts": ts.isoformat(),
                        "open": float(row["open"]),
                        "high": float(row["high"]),
                        "low": float(row["low"]),
                        "close": float(row["close"]),
                        "volume": int(row["volume"]),
                        "oi": int(row["oi"]),
                    }

                    message_tf = json.dumps(message_tf).encode("utf-8")

                    producer.produce(
                        topic=topic.name,
                        key=kafka_msg.key,
                        value=message_tf,
                    )

                    print("Message Produced", kafka_msg.value)


@flow
def fetch_priority_tickers():
    tickers = get_priority_tickers_list()

    for tick in tickers:
        data = fetch_data(tick)
        trigger_kafka_events(tick, data)
        save_data(tick, data)


@flow
def fetch_non_priority_tickers():
    tickers = get_non_priority_tickers_list()
    for tick in tickers:
        data = fetch_data(tick)
        save_data(tick, data)


if __name__ == "__main__":
    sync_instruments()

    fetch_priority_tickers.serve(
        name="fetch-priority-tickers",
        schedules=[
            RRule(
                "FREQ=MINUTELY;INTERVAL=1;BYHOUR=9,10,11,12,13,14,15,16;BYMINUTE=0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59;BYDAY=MO,TU,WE,TH,FR;BYSETPOS=-1;WKST=MO",
                timezone="Asia/Kolkata",
                slug="priority-tickers-schedule",
            )
        ],
    )

    # fetch_priority_tickers()
