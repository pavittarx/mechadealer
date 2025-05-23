from kafkalib import Signal
from sources import UpstoxBroker


def on_entry_signal(self, signal: Signal):
    # Check if the strategy has appropriate balance
    # Execute the Order
    # Check if Sl exists, add a stop order
    # Check if TP exists, add a target order
    pass


def on_exit_signal(self, signal: Signal):
    # Check if a position Exists
    # Execute Order
    # Check if SL / TP Orders exists, close them.
    pass


if __name__ == "__main__":
    pass
