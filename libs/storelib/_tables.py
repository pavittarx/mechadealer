from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Float,
    DateTime,
    CheckConstraint,
    ForeignKey,
)

from _setup import meta, engine

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
    Column("is_active", String, default="false"),
    Column("is_verified", String, default="false"),
    Column("created_at", DateTime, default="now()"),
    Column("updated_at", DateTime, default="now()"),
    extend_existing=True,
)

strategies = Table(
    "strategies",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String, unique=True),
    Column("description", String),
    Column("run_tf", String),
    Column("units", Float, default=0),
    Column("capital", Float, default=0),
    Column("capital_used", Float, default=0),
    Column("capital_remaining", Float, default=0),
    Column("leverage", Float, default=1),
    Column("pnl", Float, default=0),
    Column("unrealized_pnl", Float, default=0),
    Column("realized_pnl", Float, default=0),
    Column("is_active", String, default="false"),
    Column("created_at", DateTime, default="now()"),
    extend_existing=True,
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
    Column("units_allotted", Float, default=0),
    Column("created_at", DateTime, default="now()"),
    extend_existing=True,
)

user_strategies = Table(
    "user_strategies",
    meta,
    Column("id", Integer, primary_key=True),
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("strategy_id", Integer, ForeignKey("strategies.id")),
    Column("units", Float, default=0),
    extend_existing=True,
)

orders = Table(
    "orders",
    meta,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("strategy_id", Integer, ForeignKey("strategies.id")),
    Column("broker_id", String, unique=True),
    Column("dt", DateTime),
    Column("ticker", String),
    Column("quantity", Float),
    Column("exit_quantity", Float),
    Column("action", String),
    Column("type", String),
    Column("price", Float),
    Column("order_type", String),
    Column("capital_used", Float),
    Column("margin_used", Float),
    Column("charges", String),
    Column("is_filled", String, default="false"),
    Column("is_cancelled", String, default="false"),
    Column("is_active", String, default="true"),
    Column("ref_id", Integer, ForeignKey("orders.id")),
    Column("version", Integer),
    Column("created_at", DateTime, default="now()"),
    Column("updated_at", DateTime, default="now()"),
    extend_existing=True,
)

trade_stats = Table(
    "trade_stats",
    meta,
    Column("id", Integer, primary_key=True),
    Column("strategy_id", Integer, ForeignKey("strategies.id")),
    Column("strategy_name", String),
    Column("order_id", Integer, ForeignKey("orders.id")),
    Column("ticker", String),
    Column("pnl", Float, default=0),
    extend_existing=True,
)

meta.create_all(engine)
