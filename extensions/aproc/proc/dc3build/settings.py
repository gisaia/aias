from pydantic import BaseModel, Field
from envyaml import EnvYAML
from extensions.aproc.proc.drivers.driver_configuration import DriverConfiguration
from extensions.aproc.proc.drivers.exceptions import DriverException


class Settings(BaseModel, extra='allow'):
    arlas_url_search: str = Field(title="ARLAS URL Search (ex http://arlas-server:9999/arlas/explore/{collection}/_search?f=id:eq:{item})")
    drivers: list[DriverConfiguration] = Field(title="Configuration of the drivers")


class Configuration:
    settings: Settings | None = Field(title="aproc Ingest Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())

    @staticmethod
    def raise_if_not_valid():
        MSG = "Enrich driver configuration exception: {}"
        if Configuration.settings is None or Configuration.settings.drivers is None or len(Configuration.settings.drivers) == 0:
            raise DriverException(MSG.format("No driver configured"))
        for driver in Configuration.settings.drivers:
            driver.raise_if_not_valid()
