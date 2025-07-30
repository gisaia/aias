from aias_common.access.configuration import AccessManagerSettings, S3StorageConfiguration
from aias_common.access.storages.s3 import S3Storage
from airs.core.logger import Logger
from envyaml import EnvYAML
from pydantic import BaseModel, Field, computed_field

LOGGER = Logger.logger


class Index(BaseModel, extra="allow"):
    collection_prefix: str = Field(title="Collection prefix", description="Prefix to use for the index name: index name = prefix + collection name")
    endpoint_url: str = Field(title="Elasticsearch URL", description="URL of elasticsearch for registering the items")
    login: str | None = Field(title="ES Login", description="Elasticsearch login")
    pwd: str | None = Field(title="ES pwd", description="Elasticsearch password")


class S3AccessManagerSettings(AccessManagerSettings):
    storages: list[S3StorageConfiguration] = Field(title="S3 storage list. Only one element", description="List of configurations for the available storages", min_length=1, max_length=1)


class Settings(BaseModel, extra="allow"):
    s3: S3StorageConfiguration = Field(title="S3 Configuration", description="Configuration of the S3 bucket that will contain the STAC items and assets.")
    tmp_dir: str = Field(title="Temporary directory", description="Temporary directory in which to write files that will be deleted")
    index: Index = Field(title="", description="")
    arlaseo_mapping_url: str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/9/mapping.json"
    arlaseo_collection_url: str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/v0.0.9/collection.json"
    asset_http_endpoint_url: str | None = Field(None, title="Asset URL endpoint", description="Asset URL endpoint with placeholders for bucket and collection names (e.g. http://minio:9000/{}/{})")

    @computed_field
    @property
    def storage(self) -> S3Storage:
        return S3Storage(self.s3)


class Configuration:
    settings: Settings = Field(title="AIRS Configuration", description="ARLAS Item and Assets Registration Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
