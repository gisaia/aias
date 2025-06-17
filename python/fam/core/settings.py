from envyaml import EnvYAML
from pydantic import BaseModel, Extra, Field

from fam.core.logger import Logger

LOGGER = Logger.logger


class Settings(BaseModel, extra=Extra.allow):
    inputs_directory: str = Field(title="Input directory", description="Input directory to be explored by FAM")
    driver_configuration_file: str = Field(title="Driver file location", description="The file location containing the configurations of the ingest drivers")


class Configuration:
    settings: Settings = Field(title="FAM Configuration", description="The configuration of the File and Archive Manager")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
