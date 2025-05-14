import os
from sqlalchemy import create_engine
from sqlalchemy import (
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    CheckConstraint,
    ForeignKey,
)
from dotenv import load_dotenv

load_dotenv()

pg_conn = os.getenv("PG_CONNECTION_STRING")

if pg_conn is None:
    raise ValueError("PG_CONNECTION_STRING environment variable not set")

engine = create_engine(pg_conn, echo=True)
meta = MetaData()

users = Table(
    "users",
    meta,
    Column("id", Integer, primary_key=True),
    Column("username", String, unique=True),
    Column(
        "password",
        String,
    ),
    Column("email", String),
    Column("name", String),
    Column("capital", Float, default=0),
    Column("capital_used", Float, default=0),
    Column("capital_remaining", Float, default=0),
    Column("created_at", DateTime, default="now()"),
    Column("updated_at", DateTime, default="now()"),
    Column("is_active", String, default="false"),
    Column("is_verified", String, default="false"),
)

strategies = Table(
    "strategies",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),
    Column("description", String),
    Column("run_tf", String),
    Column("capital", Float),
    Column("capital_used", Float),
    Column("capital_remaining", Float),
    Column("leverage", Float),
    Column("unrelaized_pnl", Float),
    Column("realized_pnl", Float),
    Column("created_at", DateTime),
)

user_transactions = Table(
    "user_transactions",
    meta,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("amount", Float),
    Column(
        "type",
        String,
        CheckConstraint(
            "type IN ('deposit', 'withdrawl')", name="check_user_transactions_type"
        ),
    ),
    Column("strategy_id", Integer, ForeignKey("strategies.id")),
)

orders = Table(
    "orders",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("ticker", String),
    Column("price", Float),
    Column("quantity", Float),
    Column("action", String),
    Column("type", String),
    Column("order_type", String),
    Column("capital", Float),
    Column("capital_used", Float),
    Column("capital_remaining", Float),
    Column("leverage", Float),
    Column("charges", String),
    Column("pos_id", String),
    Column("strategy_id", String),
    Column("broker_id", String, primary_key=True),
    Column("created_at", DateTime),
)

positions = Table(
    "trades",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("strategy_id", Integer, ForeignKey("strategies.id")),
    Column("ticker", String),
    Column("entry_dt", DateTime),
    Column("exit_dt", DateTime),
    Column("quantity", Float),
    Column("direction", String),
    Column("pnl", Float),
    Column("comment", String),
    Column("leverage", Float),
    Column("created_at", DateTime),
)

meta.create_all(engine)
