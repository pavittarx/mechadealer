"""Regression tests for the monorepo layout.

Before the src-layout refactor every library root was placed directly on
sys.path by its editable install, so `db`, `store`, `users`, `main` and friends
were importable as top-level modules and collided across libraries. Importing a
library also opened database pools and Kafka connections, which meant nothing
could be imported without the whole stack running.
"""

import importlib

import pytest

LIBS = [
    "coreutils",
    "datastore",
    "kafkalib",
    "storelib",
    "strategylib",
    "brokerlib",
]

SERVICES = [
    "app_server.main",
    "datasync.main",
    "orders_management.main",
    "stats_handler.main",
    "strategy_0.main",
]

# Module names that used to leak onto sys.path from the library roots.
LEAKED_NAMES = [
    "db",
    "store",
    "users",
    "models",
    "topics",
    "typelist",
    "queries",
    "auth",
    "core",
    "sources",
    "_setup",
    "_tables",
]


@pytest.mark.parametrize("module", LIBS + SERVICES)
def test_imports_without_any_configuration(module, no_config):
    """Importing must not need env vars or reachable services."""
    importlib.import_module(module)


@pytest.mark.parametrize("name", LEAKED_NAMES)
def test_library_internals_are_not_top_level_modules(name):
    with pytest.raises(ImportError):
        importlib.import_module(name)


@pytest.mark.parametrize("module", LIBS)
def test_library_is_a_real_package(module):
    """Each library must be a package directory, not a bare module."""
    mod = importlib.import_module(module)
    assert mod.__file__ is not None
    assert mod.__file__.endswith(f"{module}/__init__.py")
