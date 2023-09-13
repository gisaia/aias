from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
from airs.logger import CustomLogger as Logger

LOGGER = Logger.get_logger()

class Driver(BaseModel, extra=Extra.allow):
    name:str                  | None = Field(title="Name of the driver")
    class_name:str            | None = Field(title="Name of the driver class")
    configuration:dict        | None = Field(title="Driver configuration")
    priority:int              | None = Field(title="Driver priority. If two drivers are eligible (supports returns a FetchRequest) then driver with highest priority will be selected over driver with lower priority.)")
    assets_dir:str            | None = Field(title="Location for storing temporary asset files")

class Settings(BaseModel, extra=Extra.allow):
    celery_broker_url:str     | None = Field(title="Celery's broker url")
    celery_result_backend:str | None = Field(title="Celery's backend")
    airs_endpoint:str       | None = Field(title="ARLAS Item Registration Service endpoint.", examples=["http://127.0.0.1:8000"])
    ingesters:list[Driver]    | None = Field(title="Driver configuration")

class Configuration:
    settings:Settings         | None = Field(title="aproc Service configuration")

    @staticmethod
    def init(configuration_file:str):
        envyaml=EnvYAML(configuration_file, strict=False)
        Configuration.settings=Settings.model_validate(envyaml.export())
