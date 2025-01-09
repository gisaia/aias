from envyaml import EnvYAML
from pydantic import BaseModel, Field

from aproc.core.logger import Logger

LOGGER = Logger.logger


class ProcessSettings(BaseModel, extra='allow'):
    name: str | None = Field(title="Name of the process")
    class_name: str | None = Field(title="Name of the process class")
    configuration: dict | None = Field(title="Process configuration")


class StorageSettings(BaseModel, extra='allow'):
    type: str = Field(title='Type of storage used')


class Settings(BaseModel, extra='allow'):
    celery_broker_url: str | None = Field(title="Celery's broker url")
    celery_result_backend: str | None = Field(title="Celery's backend")
    processes: list[ProcessSettings] = Field(title="List of processes available")
    airs_endpoint: str | None = Field(title="ARLAS Item Registration Service endpoint")
    storages: list[StorageSettings] = Field(title="List of configurations for the available storages")


class Configuration:
    settings: Settings | None = Field(title="aproc Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())
