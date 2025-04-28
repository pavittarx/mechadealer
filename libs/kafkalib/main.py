from enum import Enum
from quixstreams import Application
from quixstreams.kafka.consumer import BaseConsumer as Consumer
from quixstreams.kafka.producer import Producer

from events import DataFeedTopics
from typing import Literal
import os


broker_address = os.getenv("KAFKA_BROKER_ADDRESS")

if not broker_address:
    raise Exception(
        "[kafka]: broker address must be available on KAFKA_BROKER_ADDRESS env variable"
    )

app = Application(
    broker_address=broker_address,
)


class Topics(Enum):
    FEED_RAW = app.topic(name=DataFeedTopics.FEED_RAW.value, value_deserializer="json")
    FEED_1M = app.topic(name=DataFeedTopics.FEED_1M.value, value_deserializer="json")
    FEED_2M = app.topic(name=DataFeedTopics.FEED_2M.value, value_deserializer="json")
    FEED_5M = app.topic(name=DataFeedTopics.FEED_5M.value, value_deserializer="json")
    FEED_10M = app.topic(name=DataFeedTopics.FEED_10M.value, value_deserializer="json")
    FEED_15M = app.topic(name=DataFeedTopics.FEED_15M.value, value_deserializer="json")
    FEED_30M = app.topic(name=DataFeedTopics.FEED_30M.value, value_deserializer="json")
    FEED_1H = app.topic(name=DataFeedTopics.FEED_1H.value, value_deserializer="json")

    SIGNALS = app.topic(name="signals", value_deserializer="json")
    ORDERS = app.topic(name="orders", value_deserializer="json")


class Kafka:
    def __init__(self):
        self.app = Application(
            broker_address=broker_address,
        )

    def get_app(self):
        return self.app

    def get_producer(self):
        if not broker_address:
            raise Exception(
                "[kafka]: broker address must be available on KAFKA_BROKER_ADDRESS env variable"
            )

        return Producer(broker_address=broker_address)

    def get_consumer(
        self,
        consumer_group: str,
        auto_offset_reset: Literal["earliest", "latest", "error"] = "earliest",
    ):
        if not broker_address:
            raise Exception(
                "[kafka]: broker address must be available on KAFKA_BROKER_ADDRESS env variable"
            )

        return Consumer(
            broker_address=broker_address,
            consumer_group=consumer_group,
            auto_offset_reset=auto_offset_reset,
        )
