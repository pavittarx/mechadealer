import pytest
from kafkalib import Signal, SignalEvent, Topics
from pydantic import ValidationError


def test_market_signal_is_valid():
    signal = Signal(quantity=1, action="BUY", type="ENTRY", order_type="MARKET")

    assert signal.quantity == 1
    assert signal.limit_price is None


def test_limit_order_requires_a_price():
    """The old field_validator compared against lower-case "limit" and ran
    before limit_price was populated, so it never fired."""
    with pytest.raises(ValidationError, match="limit_price is required"):
        Signal(quantity=1, action="BUY", type="ENTRY", order_type="LIMIT")


def test_limit_order_with_a_price_is_valid():
    signal = Signal(
        quantity=1,
        action="BUY",
        type="ENTRY",
        order_type="LIMIT",
        limit_price=101.5,
    )

    assert signal.limit_price == 101.5


def test_exit_signal_does_not_require_a_position():
    """orders_management resolves exits from the strategy's open orders."""
    signal = Signal(quantity=1, action="SELL", type="EXIT", order_type="MARKET")

    assert signal.position is None


def test_signal_event_carries_strategy_and_ticker():
    event = SignalEvent(
        quantity=2,
        action="SELL",
        type="EXIT",
        order_type="MARKET",
        strategy="test-strategy",
        ticker="IDEA.NSE",
    )

    assert event.strategy == "test-strategy"
    assert event.ticker == "IDEA.NSE"
    assert event.ts


def test_invalid_action_is_rejected():
    with pytest.raises(ValidationError):
        Signal(quantity=1, action="HOLD", type="ENTRY", order_type="MARKET")  # type: ignore[arg-type]


class TestTopics:
    def test_members_are_plain_names(self):
        """Members used to hold quixstreams topics built at import, which
        needed a live broker just to import kafkalib."""
        assert Topics.FEED_1M.value == "datafeed_1M"
        assert Topics.SIGNALS.value == "signals"
        assert Topics.ORDERS.value == "orders"

    def test_feed_topics_are_addressable_by_timeframe(self):
        for tf in ["1M", "2M", "3M", "5M", "10M", "15M", "30M", "1H", "4H"]:
            assert Topics["FEED_" + tf].value == f"datafeed_{tf}"
