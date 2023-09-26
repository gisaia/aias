import logging

from uvicorn.logging import DefaultFormatter


class CustomLogger:
    logger_name = "logger"
    __logger: logging.Logger = None

    @classmethod
    def init(cls, level=logging.DEBUG):
        cls.__logger = logging.getLogger(cls.logger_name)
        cls.__logger.setLevel(level)
        cls.__logger.propagate = False

        formatter = DefaultFormatter(fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                                     datefmt="%Y-%m-%d %H:%M:%S")
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)

        cls.__logger.addHandler(console_handler)

    @classmethod
    @property
    def logger(cls):
        if cls.__logger is None:
            cls.init()
        return cls.__logger
