import logging
import os

from common.logger import CustomLogger


class Logger(CustomLogger):
    logger_name = "fam"
    level = os.getenv("FAM_LOGGER_LEVEL", logging.INFO)