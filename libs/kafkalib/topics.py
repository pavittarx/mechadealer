from enum import Enum
from setup import app


class DataFeedTopics(str, Enum):
    FEED_RAW = "datafeed_raw"
    FEED_1M = "datafeed_1M"
    FEED_2M = "datafeed_2M"
    FEED_5M = "datafeed_5M"
    FEED_10M = "datafeed_10M"
    FEED_15M = "datafeed_15M"
    FEED_30M = "datafeed_30M"
    FEED_1H = "datafeed_1H"
    FEED_4H = "datafeed_4H"


class Topics(Enum):
    FEED_RAW = app.topic(name=DataFeedTopics.FEED_RAW.value, value_deserializer="json")
    FEED_1M = app.topic(name=DataFeedTopics.FEED_1M.value, value_deserializer="json")
    FEED_2M = app.topic(name=DataFeedTopics.FEED_2M.value, value_deserializer="json")
    FEED_5M = app.topic(name=DataFeedTopics.FEED_5M.value, value_deserializer="json")
    FEED_10M = app.topic(name=DataFeedTopics.FEED_10M.value, value_deserializer="json")
    FEED_15M = app.topic(name=DataFeedTopics.FEED_15M.value, value_deserializer="json")
    FEED_30M = app.topic(name=DataFeedTopics.FEED_30M.value, value_deserializer="json")
    FEED_1H = app.topic(name=DataFeedTopics.FEED_1H.value, value_deserializer="json")
    FEED_4H = app.topic(name=DataFeedTopics.FEED_4H.value, value_deserializer="json")

    SIGNALS = app.topic(name="signals", value_deserializer="json")
    ORDERS = app.topic(name="orders", value_deserializer="json")
