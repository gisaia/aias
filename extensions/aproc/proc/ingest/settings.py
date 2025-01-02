from pydantic import BaseModel, Field
from envyaml import EnvYAML
from airs.core.models.model import Item, Role
from extensions.aproc.proc.drivers.driver_configuration import DriverConfiguration as DriverConfiguration
from extensions.aproc.proc.drivers.exceptions import DriverException


class Settings(BaseModel, extra='allow'):
    drivers: list[DriverConfiguration] = Field(title="Configuration of the drivers")
    inputs_directory: str = Field(title="Location of the archives")
    max_number_of_archive_for_ingest: int = Field(default=1000000, title="Maximum number of archives to ingest when ingesting a directory")
    aproc_endpoint: str | None = Field(title="APROC ENDPOINT")
    resource_id_hash_starts_at: int = Field(1, title="For some drivers, the resource id is the hash of the url path. Prefix can be ignored with this property.")
    alternative_asset_href_field: str | None = Field(None, title="Property field to use as an alternative to the data's href")

    def get_asset_href(self, item: Item) -> str | None:
        if self.alternative_asset_href_field:
            return item.properties[self.alternative_asset_href_field]
        data = item.assets.get(Role.data.value)
        return data.href if data else None


class Configuration:
    settings: Settings | None = Field(title="aproc Ingest Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())

    @staticmethod
    def raise_if_not_valid():
        MSG = "Ingest driver configuration exception: {}"
        if Configuration.settings is None or Configuration.settings.drivers is None or len(Configuration.settings.drivers) == 0:
            raise DriverException(MSG.format("No driver configured"))
        if Configuration.settings.aproc_endpoint is None:
            raise DriverException(MSG.format("APROC endpoint not configured"))
        if Configuration.settings.max_number_of_archive_for_ingest is None:
            raise DriverException(MSG.format("max_number_of_archive_for_ingest not configured"))
        if Configuration.settings.inputs_directory is None:
            raise DriverException(MSG.format("inputs_directory not configured"))
        if Configuration.settings.resource_id_hash_starts_at is None:
            raise DriverException(MSG.format("resource_id_hash_starts_at not configured"))
        for driver in Configuration.settings.drivers:
            driver.raise_if_not_valid()
