import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from pythonjsonlogger.json import JsonFormatter

default_text_formatter = "%(asctime)s %(levelname)s [%(name)s:%(lineno)d]: %(message)s"

default_json_formatter_fields = {
    "timestamp": "asctime",
    "level": "levelname",
    "message": "message",
    "logger_name": "name",
    "module": "module",
    "line_number": "lineno",
    "thread_name": "threadName",
    "process_id": "process",
    "filename": "filename",
    "funcName": "funcName",
}


class Logger:
    def __init__(
        self,
        app_name: str,
        level: int = logging.DEBUG,
        text_formatter_str: str = default_text_formatter,
        json_output: bool = True,  # Default to JSON for file output
    ) -> None:
        self.app_name = app_name
        self.level = level
        self.text_formatter_str = text_formatter_str
        self.json_output = json_output
        self.log_file_path = f".logs/{self.app_name}.log"

        log_dir = os.path.dirname(self.log_file_path)
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

    def get_logger(self) -> logging.Logger:
        service_logger = logging.getLogger(self.app_name)
        service_logger.setLevel(self.level)
        service_logger.propagate = False

        for handler in service_logger.handlers[:]:
            service_logger.removeHandler(handler)
            handler.close()

        # Console Handler (Text Formatted)
        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(self.level)
        console_formatter = logging.Formatter(self.text_formatter_str)
        ch.setFormatter(console_formatter)
        service_logger.addHandler(ch)

        # File Handler (JSON or Text Formatted)
        fh = TimedRotatingFileHandler(
            self.log_file_path,
            when="midnight",
            interval=1,
            backupCount=0,
            encoding="utf-8",
        )
        fh.setLevel(self.level)

        if self.json_output:
            # Using a more detailed JSON formatter
            file_formatter = JsonFormatter(
                fmt=" ".join(
                    f"%({field})s" for field in default_json_formatter_fields.values()
                ),
                rename_fields=default_json_formatter_fields,
            )
        else:
            file_formatter = logging.Formatter(self.text_formatter_str)

        fh.setFormatter(file_formatter)
        service_logger.addHandler(fh)

        return service_logger


# Example usage (to be placed in your application code):
#
# from libs.coreutils.logger import Logger
# import logging
#
# # For microservice 'orders' with JSON logging to file (default)
# order_service_logger = Logger(app_name="orders", level=logging.INFO).get_logger()
# order_service_logger.info("This is an info message from the orders service.", extra={"order_id": 123})
# order_service_logger.error("An error occurred.", extra={"error_code": 500, "details": "Connection failed"})

# # For microservice 'inventory' with text logging to file
# inventory_service_logger = Logger(app_name="inventory", json_output=False).get_logger()
# inventory_service_logger.debug("This is a debug message from the inventory service.")
