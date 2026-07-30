import os

from sqlalchemy import MetaData, create_engine
from sqlalchemy.engine import Engine

meta = MetaData()

_engine: Engine | None = None


def _with_psycopg3(url: str) -> str:
    """Pin the DBAPI to psycopg3.

    SQLAlchemy resolves a bare `postgresql://` to psycopg2, which this project
    no longer installs -- psycopg3 is already used for QuestDB. Connection
    strings stay driver-agnostic in configuration; the driver is chosen here.
    """
    for prefix in ("postgresql://", "postgres://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url[len(prefix) :]

    return url


def get_engine() -> Engine:
    """Return the shared SQLAlchemy engine, building it on first use.

    Deliberately lazy -- importing storelib must not require a reachable database.
    """
    global _engine

    if _engine is None:
        pg_conn = os.getenv("PG_CONNECTION_STRING")

        if pg_conn is None:
            raise RuntimeError("PG_CONNECTION_STRING environment variable not set")

        _engine = create_engine(_with_psycopg3(pg_conn))

    return _engine


def init_db() -> None:
    """Create any missing tables.

    Call this explicitly at service startup. It used to run on import, which
    meant importing storelib issued DDL against whatever database the
    environment happened to point at.
    """
    from . import _tables  # noqa: F401  -- registers the tables on `meta`

    meta.create_all(get_engine())


def reset_engine() -> None:
    """Drop the cached engine. Used by tests."""
    global _engine
    _engine = None
