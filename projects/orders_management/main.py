from coreutils import Logger
from kafkalib import SignalEvent
from pydantic.type_adapter import R
from sources import UpstoxBroker
from storelib import Store, Order
from typing import Any

store = Store()
log = Logger("orders_management")
logger = log.get_logger()


def _sync_order(order_id: str, order_details: Any):
    logger.info(
        f"Syncing order {order_id}",
        extra={"order_id": order_id, "order_details": order_details},
    )

    if not order_details:
        raise Exception("Order details are required.", order_id)

    order = store.get_order(broker_id=order_id)

    if not order:
        raise Exception("Order not found in store.", order_id)

    filled_quantity = order_details["filled_quantity"]
    if filled_quantity > 0:
        price = order_details["average_price"]
        capital_used = price * order_details["quantity"]
        margin_used = price * order_details["quantity"]

        order = Order(
            id=order.id,
            broker_id=order_id,
            strategy_id=order.strategy_id,
            dt=order_details["order_timestamp"],
            ticker=order.ticker,
            action=order.action,
            quantity=filled_quantity,
            price=price,
            order_type=order.order_type,
            type=order.type,
            capital_used=capital_used,
            margin_used=margin_used,
            is_filled=True,
            is_active=False,
            charges=0,
            is_cancelled=False,
        )

        store.update_order(order)


def _cancel_order(order_id: str, order_details: Any):
    if not order_details:
        raise Exception("Order Details are not provided.", order_id)

    order = store.get_order(broker_id=order_id)

    if not order:
        raise Exception("Order not found in store.", order_id)

    order = Order(
        id=order.id,
        broker_id=order_id,
        strategy_id=order.strategy_id,
        dt=order_details["order_timestamp"],
        ticker=order.ticker,
        action=order.action,
        quantity=order.quantity,
        price=order.price,
        order_type=order.order_type,
        type=order.type,
        capital_used=order.capital_used,
        margin_used=order.margin_used,
        is_filled=order.is_filled,
        charges=0,
        is_cancelled=True,
        is_active=False,
    )

    # Update order details in store
    store.update_order(order)


def handle_stop_orders(order_id: int):
    order = store.get_order(order_id)

    if not order:
        raise Exception("Order not found in store.", order_id)

    strategy = store.get_strategy(strategy_id=order.strategy_id)

    if not strategy:
        raise Exception("Strategy not found in store.", order.strategy_id)

    stop_orders = store.get_ref_orders(order.id)
    broker = UpstoxBroker(strategy=strategy.name)

    if stop_orders is None or len(stop_orders) == 0:
        return True

    is_stop_executed = False
    for stop_order in stop_orders:
        stop_order_details = broker.order_get(stop_order.broker_id)

        if not stop_order_details:
            raise Exception("Order details not found in broker.", stop_order.broker_id)

        if stop_order_details["filled_quantity"] > 0:
            is_stop_executed = True
            _sync_order(stop_order.broker_id, stop_order_details)
        else:
            _cancel_order(stop_order.broker_id, stop_order_details)

    return is_stop_executed


def on_entry_signal(signal: SignalEvent):
    logger.info(
        "[SIGNAL] on_entry_signal",
        extra={"signal": signal},
    )

    try:
        broker = UpstoxBroker(strategy=signal.strategy)

        # Check if the strategy has appropriate balance
        strategy = store.get_strategy(strategy_name=signal.strategy)
        if not strategy:
            logger.error(
                "[ENTRY] Strategy not found in store.", extra={"signal": signal}
            )
            return

        balance = strategy.capital_remaining
        if balance is None or balance <= 0:
            logger.error(
                "[ENTRY] Insufficient balance in strategy.",
                extra={"signal": signal, "strategy": strategy},
            )
            return

        required_amount = signal.quantity * broker.fetch_ticker_ltp(signal.ticker)
        if balance < required_amount:
            logger.error(
                "[ENTRY] Insufficient balance",
                extra={
                    "signal": signal,
                    "strategy": strategy,
                    "balance": balance,
                    "required": required_amount,
                },
            )
            return

        orders = broker.order_send(
            ticker=signal.ticker,
            action=signal.action,
            order_type=signal.order_type,
            quantity=signal.quantity,
        )

        if not orders:
            logger.error(
                "[ENTRY] Order Execution failed at broker.",
                extra={"signal": signal, "orders": orders},
            )
            return

        order_id = orders[0]
        order_details = broker.order_get(order_id=order_id)

        if not order_details:
            logger.error(
                "[ENTRY] Order details not found in broker.",
                extra={
                    "signal": signal,
                    "order_id": order_id,
                    "order_details": order_details,
                },
            )
            return

        entry_order = Order(
            broker_id=order_id,
            strategy_id=strategy.id,
            ticker=signal.ticker,
            action=signal.action,
            type=signal.type,
            order_type=signal.order_type,
            quantity=order_details["filled_quantity"],
            price=order_details["average_price"],
            dt=order_details["order_timestamp"],
            capital_used=order_details["average_price"] * order_details["quantity"],
            margin_used=order_details["average_price"] * order_details["quantity"],
            is_filled=True if order_details["filled_quantity"] > 0 else False,
            charges=0,
        )

        store.save_order(entry_order)
        logger.info(
            f"[ENTRY] {entry_order.id} / {entry_order.broker_id} Order executed successfully",
            extra={"entry_order": entry_order, "signal": signal},
        )

        if signal.sl:
            logger.info("[ENTRY] SL found, adding stop order", extra={"signal": signal})
            sl_diff = signal.sl * entry_order.price
            action = "SELL" if signal.action == "BUY" else "BUY"

            sl_price = (
                entry_order.price - sl_diff
                if signal.action == "BUY"
                else entry_order.price + sl_diff
            )

            sl_order = broker.order_send(
                ticker=signal.ticker,
                action=action,
                order_type="SL",
                quantity=signal.quantity,
                price=sl_price,
            )

            if not sl_order:
                logger.error(
                    "SL Order Execution failed at broker.",
                    extra={"signal": signal, "sl_order": sl_order},
                )
                return

            sl_order_details = broker.order_get(order_id=sl_order[0])

            if not sl_order_details:
                logger.error(
                    "SL Order details not found in broker.",
                    extra={"signal": signal, "sl_order": sl_order},
                )
                return

            sl_order = Order(
                broker_id=order_id,
                strategy_id=strategy.id,
                ticker=signal.ticker,
                action=action,
                type="SL",
                order_type=signal.order_type,
                quantity=signal.quantity,
                price=signal.sl,
                dt=sl_order_details["order_timestamp"],
                capital_used=0,
                margin_used=0,
                is_filled=False,
                charges=0,
            )

            store.save_order(sl_order)
            logger.info(
                "[ENTRY] SL Order executed successfully",
                extra={
                    "entry_order": entry_order,
                    "sl_order": sl_order,
                    "signal": signal,
                },
            )

        # TODO: handle adding TP orders
        if signal.tp:
            pass

    except Exception as e:
        logger.error(
            "Error processing entry signal",
            extra={
                "error": str(e),
                "signal": signal,
            },
        )


def on_exit_signal(signal: SignalEvent):
    logger.info(
        "[SIGNAL] on_exit_signal",
        extra={"event": signal},
    )

    try:
        broker = UpstoxBroker(strategy=signal.strategy)

        if signal.type != "EXIT":
            logger.error(
                "[EXIT] Signal type is not EXIT",
                extra={"event": signal},
            )
            return

        strategy = store.get_strategy(strategy_name=signal.strategy)

        if not strategy:
            logger.error(
                "[EXIT] Strategy not found in store.", extra={"signal": signal}
            )
            return

        open_orders = store.get_orders(strategy.id, "ENTRY")

        if not open_orders:
            logger.info(
                "No Open Orders found",
                extra={
                    "event": signal,
                    "open_orders": open_orders,
                    "strategy": strategy,
                },
            )
            return

        logger.info("[EXIT]: Open Orders found", extra={"open_orders": open_orders})

        is_stop_order_executed = False
        for order in open_orders:
            logger.info("[EXIT] Processing Exit Signal", extra={"order": order})

            is_stop_order_executed = handle_stop_orders(order.id)

            if not is_stop_order_executed:
                logger.info(
                    "[Exit] Stop Orders were not executed", extra={"order": order}
                )

                close_order_id = broker.order_send(
                    ticker=order.ticker,
                    action="SELL" if order.action == "BUY" else "BUY",
                    order_type=signal.order_type,
                    quantity=order.quantity,
                )

                if not close_order_id:
                    logger.error(
                        "Order Execution failed at broker.",
                        extra={"open_order": order, "close_order_id": close_order_id},
                    )
                    continue

                close_order_id = close_order_id[0]
                order_details = broker.order_get(order_id=close_order_id)

                if not order_details:
                    logger.error(
                        "Order details not found in broker.",
                        extra={"close_order_id": close_order_id, "open_order": order},
                    )
                    continue

                entry_order = Order(
                    **order.__dict__, exit_quantity=order.quantity, is_active=False
                )

                store.update_order(entry_order)

                close_order = Order(
                    broker_id=close_order_id,
                    strategy_id=strategy.id,
                    ticker=signal.ticker,
                    action=signal.action,
                    type=signal.type,
                    order_type=signal.order_type,
                    quantity=order_details["filled_quantity"],
                    price=order_details["average_price"],
                    dt=order_details["order_timestamp"],
                    capital_used=order_details["average_price"]
                    * order_details["quantity"],
                    margin_used=order_details["average_price"]
                    * order_details["quantity"],
                    is_filled=True if order_details["filled_quantity"] > 0 else False,
                    ref_id=order.id,
                    charges=0,
                )

                logger.info(
                    "[EXIT] Order exited successfully",
                    extra={
                        "order_details": order_details,
                        "entry_order": entry_order,
                        "close_order": close_order,
                    },
                )

                store.save_order(close_order)
    except Exception as e:
        logger.error(
            "Error Processing Exit Signal", extra={"error": str(e), "signal": signal}
        )


if __name__ == "__main__":
    # store.create_strategy(
    #     Strategy(
    #         id=0,
    #         description="test_strategy",
    #         run_tf="1M",
    #         name="test_strategy",
    #         capital=100,
    #         capital_remaining=100,
    #     )
    # )

    on_entry_signal(
        SignalEvent(
            strategy="test_strategy",
            ticker="IDEA.NSE",
            action="BUY",
            type="ENTRY",
            order_type="MARKET",
            quantity=1,
        ),
    )

    on_exit_signal(
        SignalEvent(
            strategy="test_strategy",
            ticker="IDEA.NSE",
            action="SELL",
            type="EXIT",
            order_type="MARKET",
            quantity=1,
        ),
    )

    pass
