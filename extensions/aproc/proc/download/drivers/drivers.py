import importlib
from airs.core.models.model import Item
from aproc.core.logger import Logger

from extensions.aproc.proc.download.drivers.driver import Driver
from extensions.aproc.proc.download.drivers.exceptions import DriverException
from extensions.aproc.proc.download.settings import \
    Configuration as DownloadSettings

LOGGER = Logger.logger


class Drivers():
    drivers: list[Driver] = None

    @staticmethod
    def init(configuration_file: str):
        DownloadSettings.init(configuration_file=configuration_file)
        Drivers.drivers = []
        for driver_configuration in DownloadSettings.settings.drivers:
            try:
                driver: Driver = importlib.import_module(driver_configuration.class_name).Driver
                driver.init(driver_configuration.configuration)
                driver.priority = driver_configuration.priority
                driver.name = driver_configuration.name
                driver.alternative_asset_href_field = driver_configuration.alternative_asset_href_field
                Drivers.drivers.append(driver)
            except ModuleNotFoundError:
                raise DriverException("Driver {} not found".format(driver_configuration.class_name))
        Drivers.drivers.sort(key=lambda driver: driver.priority)

    @staticmethod
    def solve(item: Item) -> Driver:
        Drivers.__check_drivers()
        for driver in Drivers.drivers:
            try:
                if driver.supports(item) is True:
                    return driver()
            except Exception as e:
                LOGGER.exception(e)
        return None

    @staticmethod
    def get_driver_by_name(name: str) -> Driver:
        Drivers.__check_drivers()
        for driver in Drivers.drivers:
            driver: Driver = driver
            if driver.name == name:
                return driver
        return None

    @staticmethod
    def __check_drivers():
        if Drivers.drivers is None:
            raise Exception("Drivers not initialized")
