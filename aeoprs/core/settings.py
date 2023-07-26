from enum import Enum

import yaml
from pydantic import BaseModel, Extra, Field


class S3(BaseModel):
    access_key_id:str
    secret_access_key:str
    platform:str=None
    tier:str="Standard"
    region:str
    endpoint_url:str
    asset_http_endpoint_url:str
    bucket:str

class Index(BaseModel, extra=Extra.allow):
    collection_prefix:str
    endpoint_url:str
    login:str=None
    pwd:str=None

class Settings(BaseModel, extra=Extra.allow):
    s3:S3
    index:Index

class Configuration:
    settings:Settings=None

    @staticmethod
    def init(configuration_file:str):
        with open(configuration_file) as file:
            Configuration.settings=Settings.parse_obj(yaml.load(file, Loader=yaml.FullLoader))

