from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
from agate.logger import Logger

LOGGER = Logger.logger


class Service(BaseModel, extra=Extra.allow):
    url_patterns: list[str]
    public_url_patterns: list[str] | None
    url_header: str
    url_header_prefix: str | None
    pattern_target: str | None = Field(title="If undefined, then the pattern is matched against the path. User query.{param}, where {param} is the parameter value, to use a query parameter. Use query.{param}.url.path|query if the param value is a url and that you want to target the path or query of that url.")


class Settings(BaseModel, extra=Extra.allow):
    arlas_url_search: str = Field(title="ARLAS URL Search (ex http://arlas-server:9999/arlas/explore/{collection}/_search?f=id:eq:{item})")
    agate_prefix: str
    host: str
    port: int
    services: dict[str, Service] = Field({}, title="dictionary of service name/values. Each value is a pattern configuration for extracting collection and id values for building an ARLAS request that determines whether the access is granted or not.")


class Configuration:
    settings: Settings = None

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
