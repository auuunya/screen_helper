import logging
import os
from logging.handlers import TimedRotatingFileHandler

class LoggerController:
    """
    LoggerController is a singleton class responsible for managing logging functionality.
    It supports both console and file-based logging and adapts log levels based on debug settings.
    """
    _logger = None

    @classmethod
    def setup_logger(cls, name: str, debug: bool = False, log_file: str = "engine.log"):
        """
        Configures the logger with the specified settings.

        :param name: Name of the logger.
        :param debug: Enables debug mode if set to True; otherwise uses INFO level.
        :param log_file: Name of the log file when logging to a file.
        """
        if cls._logger is None:
            cls._logger = logging.getLogger(name)
            cls._logger.setLevel(logging.DEBUG if debug else logging.INFO)
            cls._logger.propagate = False

            if cls._logger.hasHandlers():
                cls._logger.handlers.clear()

            handler = cls._get_handler(debug, log_file)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            cls._logger.addHandler(handler)

    @classmethod
    def _get_handler(cls, debug: bool, log_file: str):
        """
        Returns an appropriate logging handler based on the debug setting.

        :param debug: Determines whether to log to console or to a file.
        :param log_file: Name of the log file for file-based logging.
        :return: A logging handler instance.
        """
        if debug:
            return logging.StreamHandler()

        log_path = os.path.join(os.getcwd(), log_file)
        file_handler = TimedRotatingFileHandler(log_path, when="midnight", interval=1, backupCount=7)
        file_handler.suffix = "%Y-%m-%d"
        return file_handler

    @classmethod
    def log_info(cls, message: str):
        """
        Logs an informational message.

        :param message: The message to log.
        """
        if cls._logger:
            cls._logger.info(message)

    @classmethod
    def log_debug(cls, message: str):
        """
        Logs a debug message.

        :param message: The message to log.
        """
        if cls._logger:
            cls._logger.debug(message)

    @classmethod
    def log_error(cls, message: str):
        """
        Logs an error message.

        :param message: The message to log.
        """
        if cls._logger:
            cls._logger.error(message)
