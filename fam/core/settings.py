from envyaml import EnvYAML
from pydantic import BaseModel, Extra

from fam.core.logger import Logger

LOGGER = Logger.logger


class Settings(BaseModel, extra=Extra.allow):
    inputs_directory: str
    driver_configuration_file: str


class Configuration:
    settings: Settings = None

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
