# Core Utilities Library

This library provides common utility modules for the project.

## Logger (`logger.py`)

A flexible logging utility that supports per-application log files, daily rotation, JSON output for files, and standard text output for the console.

### Features

-   **Per-Application Logging**: Each microservice or application component can have its own dedicated log file (e.g., `.logs/my_app_name.log`).
-   **Daily Log Rotation**: Log files are rotated daily at midnight. The previous day's log file is overwritten by default.
-   **JSON File Output**: Logs written to files are in JSON format, making them easy to parse and ingest by log management systems.
    -   Supports custom fields passed via the `extra` dictionary in logging calls (e.g., `logger.info("message", extra={"custom_key": "value"})`).
-   **Text Console Output**: Logs written to the console are in a human-readable text format.
-   **Configurable**:
    -   `app_name`: Specifies the name of the application/service, used for the log filename.
    -   `level`: Sets the logging level (e.g., `logging.DEBUG`, `logging.INFO`).
    -   `json_output`: Boolean to enable/disable JSON formatting for file output (defaults to `True`).
    -   `text_formatter_str`: Allows customization of the console log format string.

### Setup

- `python-json-logger` > `2.7`
- The logger will attempt to create a `.logs` directory in your project root if it doesn't exist. Ensure your application has write permissions for this directory.

### Usage
Import the `Logger` class from `libs.coreutils.logger` and instantiate it with your application's name.

```python
from libs.coreutils.logger import Logger
import logging

# --- Example for an 'orders' microservice ---

# Get a logger instance for the 'orders' application
# File logs will be in JSON format by default
orders_logger = Logger(app_name="orders", level=logging.INFO).get_logger()

# Log messages
orders_logger.info("Orders service has started successfully.")
orders_logger.debug("Debugging order processing for order_id: 12345") # Won't show if level is INFO

# Log with extra custom fields (will appear in the JSON output)
orders_logger.info(
    "Order received",
    extra={"order_id": "ORD789", "customer_id": "CUST001", "amount": 99.99}
)
orders_logger.warning(
    "Low stock for product",
    extra={"product_id": "PROD567", "current_stock": 5}
)
orders_logger.error(
    "Failed to process payment for order",
    extra={"order_id": "ORD789", "error_code": "PMT_003", "gateway_response": "Insufficient funds"}
)

# --- Example for an 'inventory' microservice with text file output ---

# Get a logger instance for the 'inventory' application, forcing text output for files
inventory_logger = Logger(app_name="inventory", level=logging.DEBUG, json_output=False).get_logger()

inventory_logger.debug(
    "Performing inventory check for warehouse A.",
    extra={"warehouse_id": "WH_A", "items_to_check": 1500} # 'extra' still works, but output is text
)
inventory_logger.info("Inventory sync complete for warehouse A.")

