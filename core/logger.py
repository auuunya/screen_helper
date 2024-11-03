import os
import logging
from logging.handlers import TimedRotatingFileHandler

class LoggerController:
    logger = None

    @staticmethod
    def setup_logger(name: str, debug: bool = False, log_file_name: str = "screen_helper"):
        """配置日志记录器，根据 debug 设置不同的日志级别。"""
        if LoggerController.logger is None:
            LoggerController.logger = logging.getLogger(name)
            if LoggerController.logger.hasHandlers():
                LoggerController.logger.handlers.clear()
            LoggerController.logger.setLevel(logging.DEBUG if debug else logging.INFO)
            LoggerController.logger.propagate = False
            if debug:
                handler = logging.StreamHandler()
            else:
                log_file = os.path.join(os.getcwd(), f"{log_file_name}.log")
                handler = TimedRotatingFileHandler(log_file, when="midnight", interval=1, backupCount=7)
                handler.suffix = "%Y-%m-%d"
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            LoggerController.logger.addHandler(handler)

    @staticmethod
    def log_info(message: str):
        """记录信息日志"""
        if LoggerController.logger:
            LoggerController.logger.info(message)

    @staticmethod
    def log_debug(message: str):
        """记录调试日志"""
        if LoggerController.logger:
            LoggerController.logger.debug(message)

    @staticmethod
    def log_error(message: str):
        """记录错误日志"""
        if LoggerController.logger:
            LoggerController.logger.error(message)