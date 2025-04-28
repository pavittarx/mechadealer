from enum import Enum


class DataFeedTopics(str, Enum):
    FEED_RAW = "datafeed_raw"
    FEED_1M = "datafeed_1M"
    FEED_2M = "datafeed_2M"
    FEED_5M = "datafeed_5M"
    FEED_10M = "datafeed_10M"
    FEED_15M = "datafeed_15M"
    FEED_30M = "datafeed_30M"
    FEED_1H = "datafeed_1H"


class SignalTopics(str, Enum):
    ENTRY_SIGNAL = "entry_signal"
    EXIT_SIGNAL = "exit_signal"
    SL_SIGNAL = "sl_signal"
    TP_SIGNAL = "tp_signal"


class OrderTopics(str, Enum):
    ORDER_OPEN = "order_open"
    ORDER_CLOSE = "order_close"
    ORDER_SL = "order_sl"
    ORDER_TP = "order_tp"
    ORDER_CANCEL = "order_cancel"
    ORDER_MODIFY = "order_modify"
