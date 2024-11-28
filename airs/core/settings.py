from pydantic import BaseModel
from envyaml import EnvYAML
from airs.core.logger import Logger

LOGGER = Logger.logger


class S3(BaseModel):
    access_key_id: str | None = None
    secret_access_key: str | None = None
    platform: str | None = None
    tier: str = "Standard"
    region: str | None = None
    asset_http_endpoint_url: str | None = None
    endpoint_url: str | None = None
    bucket: str | None = None


class Index(BaseModel, extra="allow"):
    collection_prefix:str
    endpoint_url:str
    login:str | None
    pwd:str | None

class Settings(BaseModel, extra="allow"):
    s3:S3
    index:Index
    arlaseo_mapping_url:str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/8/mapping.json"
    arlaseo_collection_url:str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/v0.0.8/collection.json"

class Configuration:
    settings:Settings=None

    @staticmethod
    def init(configuration_file:str):
        envyaml=EnvYAML(configuration_file, strict=False)
        Configuration.settings=Settings.model_validate(envyaml.export())
