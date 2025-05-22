# mechadealer
mechadealer is a FinTech application that empowers retail investors to invest in automated trading strategies. This application that allows users to view key performance metrics of each strategy, monitor performance and adjust investments in real-time.

For a deep dive please read the docs [here](./docs/README.md)

### Technology Stack
- Python
- FastAPI

## Running Tests

This project uses `pytest` for testing. To run the tests locally:

1.  Ensure you have `pytest` and other development dependencies installed. If you are using `uv`, you can install all dependencies (including development ones) by running the following command in the root of the project:
    ```bash
    uv sync
    ```
2.  Navigate to the root directory of the project in your terminal.
3.  Run the main test script:
    ```bash
    python tests/main.py
    ```
    This script will use `pytest` to discover and run all tests in the `tests` directory.