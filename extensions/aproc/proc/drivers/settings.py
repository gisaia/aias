from typing import Generic, TypeVar
from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML


class Driver(BaseModel, extra=Extra.allow):
    name: str | None = Field(title="Name of the driver")
    class_name: str | None = Field(title="Name of the driver class")
    configuration: dict | None = Field(title="Driver configuration")
    priority: int | None = Field(title="Driver priority. If two drivers are eligible (supports returns a FetchRequest) then driver with highest priority will be selected over driver with lower priority.)")
    assets_dir: str | None = Field(title="Location for storing temporary asset files")


DRIVER = TypeVar('DRIVER', bound=Driver)


class Settings(BaseModel, Generic[DRIVER], extra='allow'):
    drivers: list[DRIVER] = Field(title="Configuration of the drivers")


SETTINGS = TypeVar('SETTINGS', bound=Settings)


class Configuration(Generic[SETTINGS]):
    settings: SETTINGS | None = Field(title="Aproc Service driver configuration")

    @staticmethod
    def init(configuration_file: str, SETTINGS):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = SETTINGS(**envyaml.export())
