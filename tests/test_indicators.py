"""Guards the pandas-ta -> pandas-ta-classic swap.

pandas-ta hard-pinned numba==0.61.2, which capped numpy at <2.3 and held pandas
on 2.x. pandas-ta-classic has the same API without that pin. These values were
captured from pandas-ta 0.4.71b0 before the swap, so a regression in the
indicator would fail here rather than silently change trading signals.
"""

import numpy as np
import pandas as pd
import pandas_ta_classic as ta
import pytest

# Deterministic input: cumulative walk from a fixed seed.
CLOSE = pd.Series(np.cumsum(np.random.default_rng(7).normal(0, 1, 300)) + 500)

# Captured from pandas-ta 0.4.71b0 on the series above, before the swap.
EXPECTED_TAIL = {
    4: 460.42184304098515,
    8: 460.06106911919255,
    20: 459.21930264760425,
}


@pytest.mark.parametrize("length", sorted(EXPECTED_TAIL))
def test_ema_matches_pre_swap_values(length):
    result = ta.ema(CLOSE, length=length)  # type: ignore[operator]

    assert result is not None
    assert result.iloc[-1] == pytest.approx(EXPECTED_TAIL[length], abs=1e-9)


@pytest.mark.parametrize("length", sorted(EXPECTED_TAIL))
def test_ema_is_sma_seeded(length):
    """pandas-ta seeds the EMA with an SMA (TA-Lib behaviour), so the first
    `length - 1` values are NaN and the seed equals the simple mean."""
    result = ta.ema(CLOSE, length=length)  # type: ignore[operator]

    assert result.iloc[: length - 1].isna().all()
    assert result.iloc[length - 1] == pytest.approx(CLOSE.iloc[:length].mean())


def test_ema_responds_faster_than_a_longer_ema_on_a_rising_series():
    rising = pd.Series(np.arange(100, dtype=float))

    fast = ta.ema(rising, length=4).iloc[-1]  # type: ignore[operator]
    slow = ta.ema(rising, length=8).iloc[-1]  # type: ignore[operator]

    assert fast > slow


def test_strategy_0_emits_signals_on_a_crossover():
    from strategy_0.main import strategyFunc

    rising = pd.DataFrame({"close": np.arange(1, 41, dtype=float)})
    signals = strategyFunc(rising)

    assert signals
    assert signals[0].action in {"BUY", "SELL"}


def test_strategy_0_needs_enough_bars():
    from strategy_0.main import strategyFunc

    thin = pd.DataFrame({"close": np.arange(1, 5, dtype=float)})

    assert strategyFunc(thin) == []
