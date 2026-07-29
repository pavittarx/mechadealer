"""Configuration must be read when a resource is first used, not at import.

Each of these used to run at module import, so any import of the library
required a full stack of env vars and reachable services.
"""

import pytest


def test_kafka_app_requires_broker_address_only_when_built(no_config):
    from kafkalib._client import get_app, reset_app

    reset_app()
    with pytest.raises(RuntimeError, match="KAFKA_BROKER_ADDRESS"):
        get_app()


def test_engine_requires_connection_string_only_when_built(no_config):
    from storelib._setup import get_engine, reset_engine

    reset_engine()
    with pytest.raises(RuntimeError, match="PG_CONNECTION_STRING"):
        get_engine()


def test_questdb_pool_requires_connection_string_only_when_built(no_config):
    from datastore.db import Database

    Database._pool = None
    with pytest.raises(RuntimeError, match="QDB_CONNECTION_STRING"):
        Database.get_pool()


def test_upstox_credentials_are_validated_on_demand(no_config):
    from brokerlib.upstox.auth import get_client_credentials

    with pytest.raises(RuntimeError, match="UPSTOX_CLIENT_ID"):
        get_client_credentials()


def test_upstox_credentials_returns_both_values(monkeypatch):
    from brokerlib.upstox.auth import get_client_credentials

    monkeypatch.setenv("UPSTOX_CLIENT_ID", "id-123")
    monkeypatch.setenv("UPSTOX_CLIENT_SECRET", "secret-456")

    assert get_client_credentials() == ("id-123", "secret-456")


def test_market_data_schema_declares_oi():
    """datasync writes `oi` and get_historic_data reads it back."""
    from datastore.db import MARKET_DATA_DDL

    assert "oi DOUBLE" in MARKET_DATA_DDL
