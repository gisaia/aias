from enum import Enum

from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
from aeoprs.logger import CustomLogger as Logger

LOGGER = Logger.get_logger()

class S3(BaseModel):
    access_key_id:str
    secret_access_key:str
    platform:str=Field(None)
    tier:str="Standard"
    region:str=Field(None)
    asset_http_endpoint_url:str
    endpoint_url:str
    bucket:str

class Index(BaseModel, extra=Extra.allow):
    collection_prefix:str
    endpoint_url:str
    login:str=Field(None)
    pwd:str=Field(None)

class Settings(BaseModel, extra=Extra.allow):
    s3:S3
    index:Index
    arlaseo_mapping_url:str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/v0.0.1/mapping.json"
    arlaseo_collection_url:str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/v0.0.1/collection.json"

class Configuration:
    settings:Settings=None

    @staticmethod
    def init(configuration_file:str):
        envyaml=EnvYAML(configuration_file, strict=False)
        Configuration.settings=Settings.model_validate(envyaml.export())
