from ._client import get_app
from .topics import Topics
from .typelist import Timeframe


class Kafka:
    def __init__(self):
        self.app = get_app()

    def get_app(self):
        return self.app

    def get_topic(self, topic: Topics, **kwargs):
        """Build a quixstreams topic from a `Topics` member."""
        return self.app.topic(name=topic.value, **kwargs)

    def get_feed_topic(self, tf: Timeframe, **kwargs):
        kwargs.setdefault("value_deserializer", "json")
        return self.get_topic(Topics["FEED_" + tf], **kwargs)
