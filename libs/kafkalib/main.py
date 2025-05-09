from typing import Literal
from setup import app
from topics import Topics


class Kafka:
    def __init__(self):
        self.app = app

    def get_app(self):
        return self.app

    def get_feed_topic(
        self, tf: Literal["1M", "2M", "5M", "10M", "15M", "30M", "1H", "4H"]
    ):
        topics_match = {
            "1M": Topics.FEED_1M.value,
            "2M": Topics.FEED_2M.value,
            "5M": Topics.FEED_5M.value,
            "10M": Topics.FEED_10M.value,
            "15M": Topics.FEED_15M.value,
            "30M": Topics.FEED_30M.value,
            "1H": Topics.FEED_1H.value,
            "4H": Topics.FEED_4H.value,
        }

        return topics_match[tf]
