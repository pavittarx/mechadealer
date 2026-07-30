from enum import Enum


class Topics(str, Enum):
    """Kafka topic names.

    Members carry the topic name only. Use `Kafka.get_topic` to turn one into a
    quixstreams topic -- building those needs a live broker, so it must not
    happen at import time.
    """

    FEED_RAW = "datafeed_raw"
    FEED_1M = "datafeed_1M"
    FEED_2M = "datafeed_2M"
    FEED_3M = "datafeed_3M"
    FEED_5M = "datafeed_5M"
    FEED_10M = "datafeed_10M"
    FEED_15M = "datafeed_15M"
    FEED_30M = "datafeed_30M"
    FEED_1H = "datafeed_1H"
    FEED_4H = "datafeed_4H"

    SIGNALS = "signals"
    ORDERS = "orders"
