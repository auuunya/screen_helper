import os
import logging
from logging.handlers import TimedRotatingFileHandler

class LoggerController:
    """
    A controller class to manage logging configuration and operations.
    """
    logger = None

    @staticmethod
    def setup_logger(name: str, debug: bool = False, log_file_name: str = "screen_helper") -> None:
        """
        Configure the logger with different levels of logging based on the debug parameter.
        :param name: The name of the logger.
        :param debug: If True, set logging level to DEBUG; otherwise, set it to INFO.
        :param log_file_name: The base name of the log file.
        """
        if LoggerController.logger is None:
            LoggerController.logger = logging.getLogger(name)
            if LoggerController.logger.hasHandlers():
                LoggerController.logger.handlers.clear()
            LoggerController.logger.setLevel(logging.DEBUG if debug else logging.INFO)
            LoggerController.logger.propagate = False
            if debug:
                # Use console output for debug logging
                handler = logging.StreamHandler()
            else:
                # Use a rotating file handler for non-debug logging
                log_file = os.path.join(os.getcwd(), f"{log_file_name}.log")
                handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
                handler.suffix = "%Y-%m-%d"
            # Set log format
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            LoggerController.logger.addHandler(handler)

    @staticmethod
    def log_info(message: str) -> None:
        """
        Log an informational message.
        :param message: The message to log.
        """
        if LoggerController.logger:
            LoggerController.logger.info(message)

    @staticmethod
    def log_debug(message: str) -> None:
        """
        Log a debug-level message.
        :param message: The message to log.
        """
        if LoggerController.logger:
            LoggerController.logger.debug(message)

    @staticmethod
    def log_error(message: str) -> None:
        """
        Log an error-level message.
        :param message: The message to log.
        """
        if LoggerController.logger:
            LoggerController.logger.error(message)
