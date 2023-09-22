import logging

from config import config

LogLevels = {
    "INFO": logging.INFO,
    "ERROR": logging.ERROR,
    "DEBUG": logging.DEBUG,
    "WARNING": logging.WARNING,
}

class Logger:
    def __init__(self, log_level=LogLevels[config.log_level]):
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        self.formatter = logging.Formatter(
            "{asctime} [{name} : {lineno}] [{levelname}]: {message}", style="{"
        )
        self.cli_handler = logging.StreamHandler()
        self.cli_handler.setFormatter(self.formatter)
        self.logger.addHandler(self.cli_handler)

    def info(self, message):
        self.logger.info(message)

    def error(self, message):
        self.logger.error(message)

    def debug(self, message):
        self.logger.debug(message)

    def warning(self, message):
        self.logger.warning(message)


logger = Logger()