import os

from quixstreams import Application

_app: Application | None = None


def get_app() -> Application:
    """Return the shared quixstreams Application, building it on first use.

    Deliberately lazy -- importing kafkalib must not require a reachable broker.
    """
    global _app

    if _app is None:
        broker_address = os.getenv("KAFKA_BROKER_ADDRESS")

        if not broker_address:
            raise RuntimeError(
                "[kafka]: broker address must be available on KAFKA_BROKER_ADDRESS env variable"
            )

        _app = Application(broker_address=broker_address)

    return _app


def reset_app() -> None:
    """Drop the cached Application. Used by tests."""
    global _app
    _app = None
