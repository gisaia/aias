from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
from agate.logger import Logger

LOGGER = Logger.logger


class Settings(BaseModel, extra=Extra.allow):
    arlas_url_search: str
    agate_prefix: str
    host: str
    port: int
    url_patterns: list[str]
    public_url_patterns: list[str]
    url_header: str
    url_header_prefix: str

class Configuration:
    settings: Settings = None

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
