"""Unit accounting for investing in and withdrawing from a strategy."""

import pytest
from storelib.store import calculate_amount_from_units, calculate_units_from_amount


class TestUnitsFromAmount:
    def test_first_investment_seeds_the_unit_price(self):
        """A strategy is created with units=0 and capital=0.

        This used to raise "Strategy units cannot be zero", so nobody could
        ever be the first investor in a strategy.
        """
        assert calculate_units_from_amount(1000, 0, 0) == 1000

    def test_zero_capital_does_not_divide_by_zero(self):
        """Only strategy_units was guarded, but the division is by capital."""
        assert calculate_units_from_amount(500, 10, 0) == 500

    def test_units_track_the_current_price(self):
        # 200 units backed by 1000 capital -> 0.2 units per currency unit
        assert calculate_units_from_amount(500, 200, 1000) == 100

    def test_small_unit_prices_keep_their_precision(self):
        """The unit price used to be rounded to 2dp before multiplying, which
        turned a ratio of 0.006 into 0.01 -- a 66% error."""
        assert calculate_units_from_amount(10_000, 6, 1000) == 60


class TestAmountFromUnits:
    def test_inverts_units_from_amount(self):
        units = calculate_units_from_amount(500, 200, 1000)

        assert calculate_amount_from_units(200, 1000, units) == 500

    def test_zero_units_is_rejected(self):
        with pytest.raises(ValueError, match="Strategy units cannot be zero"):
            calculate_amount_from_units(0, 1000, 10)

    def test_round_trip_holds_for_small_prices(self):
        units = calculate_units_from_amount(10_000, 6, 1000)

        assert calculate_amount_from_units(6, 1000, units) == 10_000


class TestTransactionTypes:
    """The user_transactions check constraint permits only these two spellings.

    withdraw_from_strategy wrote "withdraw", which the constraint rejected, so
    withdrawing from a strategy always failed.
    """

    def test_constraint_allows_exactly_deposit_and_withdrawl(self):
        from storelib._tables import user_transactions

        # Declared inline on the column, so it lives on the column's
        # constraints rather than the table's.
        constraint = next(
            c
            for c in user_transactions.c.type.constraints
            if getattr(c, "name", "") == "check_user_transactions_type"
        )
        sql = str(getattr(constraint, "sqltext", ""))

        assert "'deposit'" in sql
        assert "'withdrawl'" in sql

    def test_writers_use_only_permitted_values(self):
        import inspect

        from storelib import store, users

        permitted = {"deposit", "withdrawl"}
        written = set()

        for module in (store, users):
            for line in inspect.getsource(module).splitlines():
                stripped = line.strip()
                if stripped.startswith(("type=", 'type="')) and '"' in stripped:
                    written.add(stripped.split('"')[1])

        assert written, "expected to find transaction type literals"
        assert written <= permitted, (
            f"unpermitted transaction types: {written - permitted}"
        )
