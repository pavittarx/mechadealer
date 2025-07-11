from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import text
from typing import Literal

from .models import Strategy, Order
from _setup import engine
from _tables import (
    users,
    strategies,
    user_transactions,
    user_strategies,
    orders,
)


def calculate_units_from_amount(
    amount: float,
    strategy_units: float,
    strategy_capital: float,
) -> float:
    if strategy_units == 0:
        raise ValueError("Strategy units cannot be zero")

    units_for_one_amount = round(strategy_units / strategy_capital, 2)
    total_units = round(amount * units_for_one_amount, 2)
    return total_units


def calculate_amount_from_units(
    strategy_units: float, strategy_capital: float, units: float
) -> float:
    if strategy_units == 0:
        raise ValueError("Strategy units cannot be zero")

    return units * round(strategy_capital / strategy_units, 2)


class Store:
    def __init__(self, conn=None):
        self._conn = conn

    def _get_conn(self):
        if self._conn:
            return self._conn
        return engine.begin()  # Use global engine directly

    def create_strategy(self, strategy: Strategy):
        try:
            with self._get_conn() as conn:
                print(strategy)

                conn.execute(
                    strategies.insert().values(
                        name=strategy.name,
                        description=strategy.description,
                        run_tf=strategy.run_tf,
                        capital=strategy.capital,
                        capital_used=strategy.capital_used,
                        capital_remaining=strategy.capital_remaining,
                        leverage=strategy.leverage,
                        pnl=strategy.pnl,
                        unrealized_pnl=strategy.unrealized_pnl,
                        realized_pnl=strategy.realized_pnl,
                        is_active=True,
                    )
                )
                if self._conn is None:  # Only commit if we own the connection
                    conn.commit()
        except SQLAlchemyError as e:
            print(f"Error creating strategy: {e}")
            raise

    def invest_in_strategy(self, strategy_id: int, user_id: int, amount: float):
        if not amount or amount <= 0:
            raise ValueError("Amount must be greater than 0")

        with self._get_conn() as conn:
            try:
                query_user = users.select().where(users.c.id == user_id)
                user = conn.execute(query_user).fetchone()

                if not user:
                    raise ValueError("User not found")
                if user.capital < amount:
                    raise ValueError("Insufficient capital")

                query_strategy = strategies.select().where(
                    strategies.c.id == strategy_id
                )
                strategy = conn.execute(query_strategy).fetchone()

                if not strategy:
                    raise ValueError("Strategy not found")

                units_to_be_allotted = calculate_units_from_amount(
                    amount,
                    strategy.units,
                    strategy.capital,
                )

                query_add_transaction = user_transactions.insert().values(
                    user_id=user_id,
                    amount=amount,
                    type="deposit",
                    strategy_id=strategy_id,
                    units_allotted=units_to_be_allotted,
                    created_at="now()",
                )

                query_update_user = (
                    users.update()
                    .where(users.c.id == user_id)
                    .values(
                        capital=user.capital - amount,
                        capital_used=user.capital_used + amount,
                        capital_remaining=user.capital_remaining - amount,
                    )
                )

                query_update_strategy = (
                    strategies.update()
                    .where(strategies.c.id == strategy_id)
                    .values(
                        units=strategy.units + units_to_be_allotted,
                        capital=strategy.capital + amount,
                        capital_remaining=strategy.capital_remaining + amount,
                    )
                )

                query_user_strategy = user_strategies.select().where(
                    user_strategies.c.user_id == user_id,
                    user_strategies.c.strategy_id == strategy_id,
                )

                user_strategy = conn.execute(query_user_strategy).fetchone()

                if user_strategy is None:
                    query_insert_user_strategy = user_strategies.insert().values(
                        user_id=user_id,
                        strategy_id=strategy_id,
                        units=units_to_be_allotted,
                    )
                    conn.execute(query_insert_user_strategy)

                else:
                    query_update_user_strategy = (
                        user_strategies.update()
                        .where(
                            user_strategies.c.user_id == user_id,
                            user_strategies.c.strategy_id == strategy_id,
                        )
                        .values(
                            units=user_strategy.units + units_to_be_allotted,
                        )
                    )
                    conn.execute(query_update_user_strategy)

                conn.execute(query_add_transaction)
                conn.execute(query_update_user)
                conn.execute(query_update_strategy)

                if self._conn is None:  # Only commit if we own the connection
                    conn.commit()
            except SQLAlchemyError as e:
                print(f"Error investing in strategy: {e}")
                if self._conn is None:  # Only rollback if we own the connection
                    conn.rollback()
                raise

    def withdraw_from_strategy(self, strategy_id: int, user_id: int, amount: float):
        if not amount or amount <= 0:
            raise ValueError("Amount must be greater than 0")

        with self._get_conn() as conn:
            try:
                query_user = users.select().where(users.c.id == user_id)
                user = conn.execute(query_user).fetchone()

                if not user:
                    raise ValueError("User not found")

                query_strategy = strategies.select().where(
                    strategies.c.id == strategy_id
                )
                strategy = conn.execute(query_strategy).fetchone()

                if not strategy:
                    raise ValueError("Strategy not found")

                query_user_strategy = user_strategies.select().where(
                    user_strategies.c.user_id == user_id,
                    user_strategies.c.strategy_id == strategy_id,
                )

                user_strategy = conn.execute(query_user_strategy).fetchone()

                if not user_strategy:
                    raise ValueError("User strategy not found")

                if user_strategy.units == 0:
                    raise ValueError("No units available to withdraw")

                units_to_be_withdrawn = calculate_units_from_amount(
                    amount,
                    strategy.units,
                    strategy.capital,
                )

                if units_to_be_withdrawn > user_strategy.units:
                    raise ValueError("Insufficient units to withdraw")

                if strategy.units - units_to_be_withdrawn < 0:
                    raise ValueError("Insufficient units in strategy")

                query_add_transaction = user_transactions.insert().values(
                    user_id=user_id,
                    amount=amount,
                    type="withdraw",
                    strategy_id=strategy_id,
                    units_allotted=units_to_be_withdrawn,
                    created_at="now()",
                )

                query_update_user = (
                    users.update()
                    .where(users.c.id == user_id)
                    .values(
                        capital=user.capital + amount,
                        capital_used=user.capital_used - amount,
                        capital_remaining=user.capital_remaining + amount,
                    )
                )

                query_update_strategy = (
                    strategies.update()
                    .where(strategies.c.id == strategy_id)
                    .values(
                        units=strategy.units - units_to_be_withdrawn,
                        capital=strategy.capital - amount,
                        capital_remaining=strategy.capital_remaining - amount,
                    )
                )

                query_update_user_strategy = (
                    user_strategies.update()
                    .where(
                        user_strategies.c.user_id == user_id,
                        user_strategies.c.strategy_id == strategy_id,
                    )
                    .values(
                        units=user_strategy.units - units_to_be_withdrawn,
                    )
                )

                conn.execute(query_add_transaction)
                conn.execute(query_update_user_strategy)
                conn.execute(query_update_user)
                conn.execute(query_update_strategy)

                if self._conn is None:  # Only commit if we own the connection
                    conn.commit()
            except SQLAlchemyError as e:
                print(f"Error withdrawing from strategy: {e}")
                if self._conn is None:  # Only rollback if we own the connection
                    conn.rollback()
                raise

    def get_order(self, order_id: int | None = None, broker_id: str | None = None):
        if not order_id and not broker_id:
            raise ValueError("Either order_id or broker_id must be provided")

        try:
            with self._get_conn() as conn:
                query = orders.select().where(
                    (orders.c.id == order_id) | (orders.c.broker_id == broker_id)
                )
                result = conn.execute(query).fetchone()
                return result
        except SQLAlchemyError as e:
            print(f"Error fetching order: {e}")
            raise

    def get_orders(
        self, strategy_id: int, type: Literal["ENTRY", "EXIT", "SL", "TP"] | None = None
    ):
        if not strategy_id:
            raise ValueError("Either strategy_id or strategy_name must be provided")

        where = (orders.c.strategy_id == strategy_id) & (orders.c.is_active == "true")

        if type:
            where = where & (orders.c.type == type)

        try:
            with self._get_conn() as conn:
                query = orders.select().where(where)
                result = conn.execute(query).fetchall()
                return result
        except SQLAlchemyError as e:
            print(f"Error fetching open orders: {e}")
            raise

    def get_ref_orders(self, ref_id: str):
        if not ref_id:
            raise ValueError("ref_id must be provided")

        try:
            with self._get_conn() as conn:
                query = orders.select().where(
                    (orders.c.ref_id == ref_id) & (orders.c.is_active == "true")
                )
                result = conn.execute(query).fetchall()
                return result
        except SQLAlchemyError as e:
            print(f"Error fetching orders by ref_id: {e}")
            raise

    def save_order(self, order: Order):
        try:
            with self._get_conn() as conn:
                conn.execute(
                    orders.insert().values(
                        strategy_id=order.strategy_id,
                        broker_id=order.broker_id,
                        dt=order.dt,
                        ticker=order.ticker,
                        quantity=order.quantity,
                        exit_quantity=0,
                        action=order.action,
                        type=order.type,
                        price=order.price,
                        order_type=order.order_type,
                        capital_used=order.capital_used,
                        margin_used=order.margin_used,
                        charges=order.charges,
                        ref_id=order.ref_id,
                        version=1,
                        is_filled=order.is_filled,
                        is_cancelled=order.is_cancelled,
                        is_active=order.is_active,
                    )
                )
                if self._conn is None:  # Only commit if we own the connection
                    conn.commit()
        except SQLAlchemyError as e:
            print(f"Error saving order: {e}")
            raise

    def update_order(self, order):
        if not order.id:
            raise ValueError("Order ID must be provided")

        with self._get_conn() as conn:
            try:
                query_order = orders.select().where(
                    (orders.c.id == order.id) | (orders.c.broker_id == order.broker_id)
                )

                order_details = conn.execute(query_order).fetchone()

                if not order_details:
                    raise ValueError("Order not found")

                if order.id and order.id != order_details.id:
                    raise ValueError("Order ID does not match the fetched order")

                if order.broker_id != order_details.broker_id:
                    raise ValueError("Broker ID does not match the fetched order")

                query = (
                    orders.update()
                    .where((orders.c.id == order.id))
                    .values(
                        price=order.price,
                        quantity=order.quantity,
                        exit_quantity=order.exit_quantity,
                        is_filled=order.is_filled,
                        capital_used=order.capital_used,
                        margin_used=order.margin_used,
                        is_cancelled=order.is_cancelled,
                        is_active=order.is_active,
                        version=(order_details.version or 1) + 1,
                        updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    )
                )
                conn.execute(query)
                if self._conn is None:  # Only commit if we own the connection
                    conn.commit()
            except SQLAlchemyError as e:
                print(f"Error updating order: {e}")
                if self._conn is None:  # Only rollback if we own the connection
                    conn.rollback()
                raise

    def get_strategy(
        self, strategy_id: int | None = None, strategy_name: str | None = None
    ):
        if not strategy_id and not strategy_name:
            raise ValueError("Either strategy_id or strategy_name must be provided")

        try:
            with self._get_conn() as conn:
                query = strategies.select().where(
                    (strategies.c.id == strategy_id)
                    | (strategies.c.name == strategy_name)
                )
                result = conn.execute(query).fetchone()
                return result
        except SQLAlchemyError as e:
            print(f"Error fetching strategy: {e}")
            raise

    def get_strategies(self):
        try:
            with self._get_conn() as conn:
                query = strategies.select()
                result = conn.execute(query).fetchall()
                return result
        except SQLAlchemyError as e:
            print(f"Error fetching strategies: {e}")
            raise

    def get_user_strategies(self, user_id: int):
        if not user_id:
            raise ValueError("user_id must be provided")

        try:
            with self._get_conn() as conn:
                query_text = f"""
                    SELECT * from strategies s
                    JOIN user_strategies us ON s.id = us.strategy_id
                    WHERE us.user_id = {user_id};
                """

                stmt = text(query_text)
                result = conn.execute(stmt).fetchall()
                return result

        except SQLAlchemyError as e:
            print(f"Error fetching strategies: {e}")
            raise
