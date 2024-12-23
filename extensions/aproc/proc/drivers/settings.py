from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML


class Driver(BaseModel, extra=Extra.allow):
    name: str | None = Field(title="Name of the driver")
    class_name: str | None = Field(title="Name of the driver class")
    configuration: dict | None = Field(title="Driver configuration")
    priority: int | None = Field(title="Driver priority. If two drivers are eligible (supports returns a FetchRequest) then driver with highest priority will be selected over driver with lower priority.)")
    assets_dir: str | None = Field(title="Location for storing temporary asset files")


class Settings(BaseModel, extra='allow'):
    drivers: list[Driver] = Field(title="Configuration of the drivers")


class Configuration:
    settings: Settings | None = Field(title="aproc Ingest Service configuration")

    @staticmethod
    def init(configuration_file: str, settingsClass):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = settingsClass(**envyaml.export())
