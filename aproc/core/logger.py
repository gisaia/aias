import logging
import os

from aias_common.logger import CustomLogger


class Logger(CustomLogger):
    logger_name = "aproc"
    level = os.getenv("APROC_LOGGER_LEVEL", logging.INFO)
