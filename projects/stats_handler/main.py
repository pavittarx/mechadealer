from coreutils import Logger
from storelib import Store
from brokerlib import UpstoxBroker

log = Logger("stats_handler")
logger = log.get_logger()
store = Store()


def main():
    broker = UpstoxBroker("stats_handler")
    strategies = store.get_strategies()
    strategies = [strategy._mapping for strategy in strategies]
    strategies = list(filter(lambda x: x["is_active"] == "true", strategies))

    for strategy in strategies:
        orders = store.get_orders(strategy["id"], type="ENTRY")

        if not orders:
            logger.info(f"No orders found for strategy {strategy['id']}")
            continue

        orders = [order._mapping for order in orders]

        tickers = set(map(lambda x: x["ticker"], orders))

        for tick in tickers:
            unrealized_pnl = 0.0
            realized_pnl = 0.0

            orders_for_ticker = list(filter(lambda x: x["ticker"] == tick, orders))
            if not orders_for_ticker:
                continue

            running_orders = list(
                filter(
                    lambda x: x["exit_quantity"] == 0 and x["is_filled"] == "true",
                    orders_for_ticker,
                )
            )

            ltp = broker.fetch_ticker_ltp(tick)

            def calc_unrealized_pnl(order):
                pnl = (ltp * float(order["quantity"])) - (
                    float(order["price"]) * float(order["quantity"])
                    + float(order["charges"])
                )

                if order["action"] == "SELL":
                    pnl *= -1

                return pnl

            unrealized_pnl += sum(
                map(
                    calc_unrealized_pnl,
                    running_orders,
                )
            )

            executed_orders = list(
                filter(
                    lambda x: x["exit_quantity"] == x["quantity"]
                    and x["is_filled"] == "true",
                    orders_for_ticker,
                )
            )

            for order in executed_orders:
                ref_orders = store.get_ref_orders(order.id)
                ref_orders = [x._mapping for x in ref_orders]

                if not ref_orders:
                    continue

                ref_order = list(
                    filter(lambda x: x["is_filled"] == "true", ref_orders)
                )[0]

                if not ref_order:
                    logger.warning(f"No filled reference order found for {order.id}")
                    continue

                pnl = (ref_order["price"] * ref_order["quantity"]) - (
                    order["price"] * order["quantity"] + order["charges"]
                )

                if order["action"] == "SELL":
                    pnl *= -1

                realized_pnl += pnl

            print(unrealized_pnl, realized_pnl)


if __name__ == "__main__":
    logger.info("[Stats Handler]: Started")
    main()
