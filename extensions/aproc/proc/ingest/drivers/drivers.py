import importlib

from extensions.aproc.proc.ingest.drivers.driver import Driver
from extensions.aproc.proc.ingest.drivers.exceptions import DriverException
from extensions.aproc.proc.ingest.settings import \
    Configuration as IngestSettings


class Drivers():
    drivers: list[Driver] = None

    @staticmethod
    def init(configuration_file: str):
        IngestSettings.init(configuration_file=configuration_file)
        Drivers.drivers = []
        for driver_configuration in IngestSettings.settings.drivers:
            try:
                driver: Driver = importlib.import_module(driver_configuration.class_name).Driver
                driver.init(driver_configuration.configuration)
                driver.priority = driver_configuration.priority
                driver.name = driver_configuration.name
                driver.__assets_dir__ = driver_configuration.assets_dir
                Drivers.drivers.append(driver)
            except ModuleNotFoundError:
                raise DriverException("Driver {} not found".format(driver_configuration.class_name))
        Drivers.drivers.sort(key=lambda driver: driver.priority)

    @staticmethod
    def solve(url: str) -> Driver:
        Drivers.__check_drivers()
        for driver in Drivers.drivers:
            if driver.supports(url) is True:
                return driver()
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