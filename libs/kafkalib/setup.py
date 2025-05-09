import os

from quixstreams import Application

broker_address = os.getenv("KAFKA_BROKER_ADDRESS")

if not broker_address:
    raise Exception(
        "[kafka]: broker address must be available on KAFKA_BROKER_ADDRESS env variable"
    )


app = Application(
    broker_address=broker_address,
)
