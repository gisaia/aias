import logging
from common.logger import CustomLogger


class Logger(CustomLogger):
    logger_name = "fam"

    @classmethod
    def init(cls, level=logging.DEBUG):
        super().init(level)
