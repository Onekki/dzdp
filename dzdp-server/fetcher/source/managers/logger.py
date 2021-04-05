import logging
import logging.handlers

from fetcher.source import utils


class LoggerManager:
    def __init__(self, filename):
        directory = utils.make_dirs("/outputs")

        self._logger = logging.getLogger()
        self._logger.setLevel(logging.INFO)
        formatter = logging.Formatter("%(asctime)s - %(process)d-%(threadName)s - "
                                      "%(module)s/%(filename)s:%(lineno)s[%(funcName)s] - %(levelname)s: %(message)s")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        file_handler = logging.handlers.RotatingFileHandler(
            directory + "/" + filename + ".log", maxBytes=10485760, backupCount=5, encoding="utf-8")
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    @property
    def logger(self):
        return self._logger
