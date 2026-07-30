import os

import pytest

CONFIG_ENV_VARS = [
    "QDB_CONNECTION_STRING",
    "QDB_CLIENT_CONF",
    "PG_CONNECTION_STRING",
    "KAFKA_BROKER_ADDRESS",
    "JWT_SECRET",
    "UPSTOX_CLIENT_ID",
    "UPSTOX_CLIENT_SECRET",
    "MECHADEALER_HOME",
]


@pytest.fixture
def no_config(monkeypatch):
    """Run with every configuration variable unset.

    A developer's .env must not be able to make these tests pass.
    """
    for var in CONFIG_ENV_VARS:
        monkeypatch.delenv(var, raising=False)


@pytest.fixture(autouse=True)
def isolated_home(monkeypatch, tmp_path):
    """Keep credential and log writes inside the test's tmp directory."""
    monkeypatch.setenv("MECHADEALER_HOME", str(tmp_path / "mechadealer"))
    yield
    os.environ.pop("MECHADEALER_HOME", None)
