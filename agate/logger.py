import logging
import os

from common.logger import CustomLogger


class Logger(CustomLogger):
    logger_name = "agate"
    level = os.getenv("AGATE_LOGGER_LEVEL", logging.INFO)
