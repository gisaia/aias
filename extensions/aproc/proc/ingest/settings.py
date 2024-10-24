from envyaml import EnvYAML
from pydantic import BaseModel, Extra, Field


class Driver(BaseModel, extra=Extra.allow):
    name: str | None = Field(title="Name of the driver")
    class_name: str | None = Field(title="Name of the driver class")
    configuration: dict | None = Field(title="Driver configuration")
    priority: int | None = Field(title="Driver priority. If two drivers are eligible (supports returns a FetchRequest) then driver with highest priority will be selected over driver with lower priority.)")
    assets_dir: str | None = Field(title="Location for storing temporary asset files")


class Settings(BaseModel, extra='allow'):
    drivers: list[Driver] = Field(title="Configuration of the drivers")
    inputs_directory: str = Field(title="Location of the archives")
    max_number_of_archive_for_ingest: int = Field(default=1000000, title="Maximum number of archives to ingest when ingesting a directory")
    aproc_endpoint: str | None = Field(title="APROC ENDPOINT")
    resource_id_hash_starts_at: int = Field(1, title="For some drivers, the resource id is the hash of the url path. Prefix can be ignored with this property.")


class Configuration:
    settings: Settings | None = Field(title="aproc Ingest Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())
