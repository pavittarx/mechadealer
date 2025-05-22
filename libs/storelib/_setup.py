import os
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
)
from dotenv import load_dotenv

load_dotenv()

pg_conn = os.getenv("PG_CONNECTION_STRING")

if pg_conn is None:
    raise ValueError("PG_CONNECTION_STRING environment variable not set")

engine = create_engine(pg_conn)
meta = MetaData()
