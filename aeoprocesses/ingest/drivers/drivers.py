from aeoprocesses.settings import Configuration
from aeoprocesses.ingest.drivers.driver import Driver
from aeoprocesses.ingest.drivers.exceptions import DriverException
import importlib

class Drivers():
    drivers:list=None

    @staticmethod
    def init():
        Drivers.drivers=[]
        for driver_configuration in Configuration.settings.ingesters:
            try:
                driver:Driver=importlib.import_module(driver_configuration.class_name).Driver
                driver.init(driver_configuration.configuration)
                driver.priority=driver_configuration.priority
                driver.name=driver_configuration.name
                driver.__assets_dir__=driver_configuration.assets_dir
                Drivers.drivers.append(driver)
            except ModuleNotFoundError as e:
                raise DriverException("Driver {} not found".format(driver_configuration.class_name))
        Drivers.drivers.sort(key=lambda driver:driver.priority)

    def solve(url: str)->Driver:
        for driver in Drivers.drivers:
            if driver.supports(url) is True:
                return driver()
        return None

    def get_driver_by_name(name: str)->Driver:
        for driver in Drivers.drivers:
            driver:Driver=driver
            if driver.name == name: return driver
        return None
