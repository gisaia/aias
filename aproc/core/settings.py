from pydantic import BaseModel, Field
from envyaml import EnvYAML
from common.logger import CustomLogger as Logger

LOGGER = Logger.get_logger()


class ProcessSettings(BaseModel, extra='allow'):
    name: str | None = Field(title="Name of the process")
    class_name: str | None = Field(title="Name of the process class")
    configuration: dict | None = Field(title="Process configuration")


class Settings(BaseModel, extra='allow'):
    celery_broker_url: str | None = Field(title="Celery's broker url")
    celery_result_backend: str | None = Field(title="Celery's backend")
    processes: list[ProcessSettings] = Field(title="List of processes available")


class Configuration:
    settings: Settings | None = Field(title="aproc Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())