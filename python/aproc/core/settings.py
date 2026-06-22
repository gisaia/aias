from envyaml import EnvYAML
from pydantic import BaseModel, Field

from aias_common.access.configuration import AccessManagerSettings
from aproc.core.logger import Logger

LOGGER = Logger.get_logger()
DEFAULT_PROCESS_QUEUE_NAME = "aproc_default_queue"


class ProcessSettings(BaseModel, extra='allow'):
    name: str | None = Field(title="Process Name", description="Name of the process")
    class_name: str | None = Field(title="Process class", description="Name of the process class")
    configuration: dict | None = Field(title="Process configuration", description="Configuration that is specific the process (dictionary key/value)")
    queue_name: str = Field(default=DEFAULT_PROCESS_QUEUE_NAME, title="Process queue name", description="Name of the queue to use for this process")
    enabled: bool = Field(default=True, title="Process enabled", description="Whether the process is enabled or not")


class Settings(BaseModel, extra='allow'):
    celery_broker_url: str = Field(title="Celery's broker url", description="Celery's broker url of the form of transport://userid:password@hostname:port/virtual_host")
    celery_result_backend: str = Field(title="Celery's backend", description="Celery's backend used to store task results")
    celery_result_backend_transport_options: dict | None = Field({}, title="Transport options", description="Celery's result backend transport options", examples="master_name: mymaster and sentinel_password: your-strong-password")
    processes: list[ProcessSettings] = Field(title="List of processes", description="List of APROC processes")
    airs_endpoint: str | None = Field(title="AIRS endpoint", description="ARLAS Item Registration Service endpoint")
    access_manager: AccessManagerSettings = Field(title="AccessManager configuration", description="Configuration for the AccessManager")
    subscriber_post_timeout: float = Field(default=10, title="Http post request timeout for subscriber notifications")


class Configuration:
    settings: Settings = Field(title="APROC Service configuration", description="The configuration of the APROC Service")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings(**envyaml.export())
