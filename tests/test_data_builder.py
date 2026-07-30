import pandas as pd
import pytest
from strategylib.data_builder import DataBuilder

BAR = {
    "ts": "2025-01-01T09:15:00",
    "open": 100.0,
    "high": 105.0,
    "low": 99.0,
    "close": 104.0,
    "volume": 1000,
    "oi": 0,
}


def test_starts_empty_for_each_ticker():
    builder = DataBuilder(["IDEA.NSE", "TATASTEEL.NSE"])

    assert builder.get_data("IDEA.NSE").empty
    assert builder.get_data("TATASTEEL.NSE").empty


def test_add_data_appends_a_bar():
    builder = DataBuilder(["IDEA.NSE"])
    builder.add_data("IDEA.NSE", BAR)

    df = builder.get_data("IDEA.NSE")

    assert len(df) == 1
    assert df.iloc[0]["close"] == 104.0


def test_add_data_accumulates_in_order():
    builder = DataBuilder(["IDEA.NSE"])
    builder.add_data("IDEA.NSE", BAR)
    builder.add_data("IDEA.NSE", {**BAR, "ts": "2025-01-01T09:16:00", "close": 106.0})

    df = builder.get_data("IDEA.NSE")

    assert len(df) == 2
    assert list(df["close"]) == [104.0, 106.0]


def test_unknown_ticker_is_rejected():
    builder = DataBuilder(["IDEA.NSE"])

    with pytest.raises(ValueError, match="not found in data store"):
        builder.add_data("RELIANCE.NSE", BAR)


def test_init_ticker_data_replaces_the_frame():
    builder = DataBuilder(["IDEA.NSE"])
    seed = pd.DataFrame([BAR]).set_index("ts")

    builder.init_ticker_data("IDEA.NSE", seed)

    assert len(builder.get_data("IDEA.NSE")) == 1


def test_init_ticker_data_rejects_unknown_ticker():
    builder = DataBuilder(["IDEA.NSE"])

    with pytest.raises(ValueError, match="not found in data store"):
        builder.init_ticker_data("RELIANCE.NSE", pd.DataFrame([BAR]).set_index("ts"))
