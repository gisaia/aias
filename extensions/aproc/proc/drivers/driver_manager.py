import importlib

from extensions.aproc.proc.drivers.abstract_driver import AbstractDriver
from extensions.aproc.proc.drivers.exceptions import DriverException
from extensions.aproc.proc.drivers.driver_configuration import DriverConfiguration
from aproc.core.logger import Logger

LOGGER = Logger.logger


class DriverManager():
    drivers: dict[str, list[AbstractDriver]] = {}

    @staticmethod
    def init(process: str, drivers: list[DriverConfiguration]):
        DriverManager.drivers[process] = []
        for driver_configuration in drivers:
            try:
                driver_class: AbstractDriver = importlib.import_module(driver_configuration.class_name).Driver
                driver_class.init(driver_configuration.configuration)
                driver_class.priority = driver_configuration.priority
                driver_class.name = driver_configuration.name
                driver_class.assets_dir = driver_configuration.assets_dir
                DriverManager.drivers[process].append(driver_class)
            except ModuleNotFoundError:
                raise DriverException("Driver {} not found".format(driver_configuration.class_name))
        DriverManager.drivers[process].sort(key=lambda driver: driver.priority)
        for driver in DriverManager.drivers[process]:
            LOGGER.info("{}: {}".format(driver.priority, driver.name))

    @staticmethod
    def driver_names(process: str) -> list[str]:
        return list(map(lambda p: p.name, DriverManager.drivers[process]))

    @staticmethod
    def solve(process: str, resource, include_drivers: list[str] = [], exclude_drivers: list[str] = []) -> AbstractDriver:
        DriverManager.__check_drivers(process)
        drivers = DriverManager.drivers.get(process, [])
        if include_drivers and len(include_drivers) > 0:
            LOGGER.debug("keep only {}".format(include_drivers))
            drivers = list(filter(lambda driver_class: driver_class.name in include_drivers, drivers))
        if exclude_drivers and len(exclude_drivers) > 0:
            LOGGER.debug("exclude {}".format(exclude_drivers))
            drivers = list(filter(lambda driver_class: driver_class.name not in exclude_drivers, drivers))
        for driver_class in drivers:
            try:
                LOGGER.debug("Test if driver {} supports the resource".format(driver_class.name))
                driver: AbstractDriver = driver_class()
                if driver.supports(resource) is True:
                    return driver
            except Exception as e:
                LOGGER.exception(e)
        return None

    @staticmethod
    def __check_drivers(process: str):
        MSG = "Ingest driver configuration exception: {}"
        if DriverManager.drivers is None or DriverManager.drivers.get(process) is None or len(DriverManager.drivers.get(process)) == 0:
            raise DriverException(MSG.format("No driver configured"))
        for driver in DriverManager.drivers.get(process):
            MSG_DRIVER = MSG.format("invalid configuration for driver {}: {}")
            if driver.assets_dir is None:
                raise DriverException(MSG_DRIVER.format("assets_dir not configured"))
            if driver.name is None:
                raise DriverException(MSG_DRIVER.format("name not configured"))
            if driver.priority is None:
                raise DriverException(MSG_DRIVER.format("priority not configured"))
