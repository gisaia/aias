from pydantic import BaseModel, Field
from envyaml import EnvYAML
from airs.core.logger import Logger

LOGGER = Logger.logger


class S3(BaseModel):
    access_key_id: str | None = Field(None, title="Access key", description="S3 access key")
    secret_access_key: str | None = Field(None, title="Secret", description="S3 access secret")
    platform: str | None = Field(None, title="Platform", description="S3 platform (ALIBABA, AWS, AZURE, GCP, IBM, ORACLE, OTHER)")
    tier: str = Field("Standard", title="Storage tiers", description="Cloud Provider Storage Tiers (Standard, Glacier, etc.)")
    region: str | None = Field(None, title="Storage region", description="The region where the data is stored. Relevant to speed of access and inter region egress costs (as defined by PaaS provider)")
    asset_http_endpoint_url: str | None = Field(None, title="Asset URL endpoint", description="Asset URL endpoint with placeholders for bucket and collection names (e.g. http://minio:9000/{}/{})")
    endpoint_url: str | None = Field(None, title="URL endpoint", description="URL endpoint (e.g. http://minio:9000)")
    bucket: str | None = Field(None, title="Bucket name", description="Bucket name")
    writable_paths: list[str] = Field(default=[], title="Writable Paths", description="List of paths where files can be written")
    readable_paths: list[str] = Field(default=[], title="Readable Paths", description="List of paths from which files can be read")


class Index(BaseModel, extra="allow"):
    collection_prefix: str = Field(title="Collection prefix", description="Prefix to use for the index name: index name = prefix + collection name")
    endpoint_url: str = Field(title="Elasticsearch URL", description="URL of elasticsearch for registering the items")
    login: str | None = Field(title="ES Login", description="Elasticsearch login")
    pwd: str | None = Field(title="ES pwd", description="Elasticsearch password")


class Settings(BaseModel, extra="allow"):
    s3: S3 = Field(title="S3 Configuration", description="Configuration of the S3 bucket that will contain the STAC items and assets.")
    index: Index = Field(title="", description="")
    arlaseo_mapping_url: str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/v1.1.0/mapping.json"
    arlaseo_collection_url: str = "https://raw.githubusercontent.com/gisaia/ARLAS-EO/v1.1.0/collection.json"


class Configuration:
    settings: Settings = Field(title="AIRS Configuration", description="ARLAS Item and Assets Registration Service configuration")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
