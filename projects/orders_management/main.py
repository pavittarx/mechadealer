import json
from coreutils import Logger
from sources import UpstoxBroker
from storelib import Store, Order
from kafkalib import Kafka, Topics, SignalEvent
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
    logger.info(f"[STOP] Handling Stop Orders for {order_id}")
    order = store.get_order(order_id)

    if not order:
        logger.error("Order not found in store.", order_id)
        return

    strategy = store.get_strategy(strategy_id=order.strategy_id)

    if not strategy:
        logger.error(
            "Strategy not found in store.", extra={"order_id": order_id, "order": order}
        )
        return

    stop_orders = store.get_ref_orders(order.id)
    broker = UpstoxBroker(strategy=strategy.name)

    if stop_orders is None or len(stop_orders) == 0:
        logger.info("No Stop Orders found for the order.", extra={"order": order})
        return False

    logger.info(
        "Stop Orders found",
        extra={"order_id": order, "order": order, "stop_orders": stop_orders},
    )

    is_stop_executed = False
    for stop_order in stop_orders:
        stop_order_details = broker.order_get(stop_order.broker_id)

        if not stop_order_details:
            logger.error("Order details not found in broker.", stop_order.broker_id)
            continue

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
                charges=0,
                ref_id=entry_order.id,
                is_cancelled=False,
                is_filled=False,
                is_active=True,
            )

            store.save_order(sl_order)
            logger.info(
                "[ENTRY] SL Order placed successfully",
                extra={
                    "entry_order": entry_order,
                    "sl_order": sl_order,
                    "signal": signal,
                },
            )

        if signal.tp:
            logger.info("[ENTRY] SL found, adding stop order", extra={"signal": signal})
            tp_diff = signal.tp * entry_order.price
            action = "SELL" if signal.action == "BUY" else "BUY"
            target_price = entry_order.price + tp_diff

            target_order = broker.order_send_gtt(
                ticker=signal.ticker,
                action=action,
                price=target_price,
                quantity=signal.quantity,
                trigger_type="IMMEDIATE",
            )

            if not target_order:
                logger.error(
                    "Target Order Execution failed at broker.",
                    extra={"signal": signal, "target_order": target_order},
                )
                return

            target_order_details = broker.order_get_gtt(order_id=target_order[0])

            target_order = Order(
                broker_id=target_order[0],
                strategy_id=strategy.id,
                ticker=signal.ticker,
                action=action,
                type="TP",
                order_type="GTT",
                quantity=signal.quantity,
                price=target_price,
                dt=target_order_details["order_timestamp"],
                capital_used=0,
                margin_used=0,
                ref_id=entry_order.id,
                is_cancelled=False,
                is_filled=False,
                is_active=True,
                charges=0,
            )

            store.save_order(target_order)
            logger.info(
                "[ENTRY] Target Order placed successfully",
            )

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
                    order_type="MARKET",
                    quantity=order.quantity,
                )

                if not close_order_id:
                    logger.error(
                        "Order Execution failed at broker.",
                        extra={"open_order": order, "close_order_id": close_order_id},
                    )

                close_order_id = close_order_id[0]
                order_details = broker.order_get(order_id=close_order_id)

                if not order_details:
                    logger.error(
                        "Order details not found in broker.",
                        extra={"close_order_id": close_order_id, "open_order": order},
                    )

                entry_order = Order(
                    id=order.id,
                    broker_id=order.broker_id,
                    strategy_id=order.strategy_id,
                    dt=str(order.dt.timestamp()),
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
                    is_cancelled=False,
                    is_active=True,
                )

                entry_order.exit_quantity = order.quantity
                entry_order.is_active = False

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
                    capital_used=(
                        order_details["average_price"] * order_details["quantity"]
                    ),
                    margin_used=(
                        order_details["average_price"] * order_details["quantity"]
                    ),
                    is_filled=True if order_details["filled_quantity"] > 0 else False,
                    ref_id=entry_order.id,
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
        print(e)
        logger.error(
            "Error Processing Exit Signal", extra={"error": str(e), "signal": signal}
        )


def init_broker():
    try:
        # Triggers Auth Flow, if token is expired or unavailable
        UpstoxBroker("orders_management_init")
    except Exception as e:
        logger.error("Error initializing broker", extra={"error": str(e)})
        raise e


if __name__ == "__main__":
    try:
        k = Kafka()
        app = k.get_app()

        init_broker()

        with app.get_consumer() as consumer:
            consumer.subscribe([Topics.SIGNALS.value.name])
            logger.info("[Order Management]: Ready")

            while True:
                res = consumer.poll(1)

                if res is None or res.value() is None:
                    # print("No Signals")
                    continue

                value = res.value().decode("utf-8")
                data = json.loads(value)

                if data["type"] == "ENTRY":
                    signal = SignalEvent.model_validate(data)
                    on_entry_signal(signal)

                elif data["type"] == "EXIT":
                    signal = SignalEvent.model_validate(data)
                    on_exit_signal(signal)

    except Exception as e:
        logger.error("Error in orders management", extra={"error": str(e)})
