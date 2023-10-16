import logging
import os

from common.logger import CustomLogger


class Logger(CustomLogger):
    logger_name = "airs"
    level = os.getenv("AIRS_LOGGER_LEVEL", logging.INFO)
