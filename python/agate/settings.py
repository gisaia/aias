from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
from agate.logger import Logger
from agate.roles_model import Roles
import yaml

LOGGER = Logger.logger


class Service(BaseModel, extra=Extra.allow):
    url_patterns: list[str] = Field(title="Pattern list", description="List of patterns for the service for extracting the collection name and item name (e.g. (?P<collection>[^/]+)/items/(?P<item>[^/]+)/assets/overview)")
    public_url_patterns: list[str] | None = Field(title="Public pattern list", description="List of patterns for public access. IMPORTANT: no access control done on those patterns.")
    url_header: str = Field(title="URL Header", description="Header containing the URL")
    url_header_prefix: str | None = Field(title="URL Prefix", description="URL prefix that is removed before pattern matching.")
    pattern_target: str | None = Field(title="If undefined, then the pattern is matched against the path. Use query.{param}, where {param} is the parameter value, to use a query parameter. Use query.{param}.url.path|query if the param value is a url and that you want to target the path or query of that url.")


class URBAC(BaseModel, extra=Extra.allow):
    url_header: str = Field(title="URL Header", description="The header containing the requested URL")
    method_header: str = Field(title="Method header", description="The header containing the method")
    jwt_header: str = Field(title="JWT Header", description="The header containing the JWT (can start with 'Bearer')")
    roles: Roles = Field(default=Roles(technicalRoles={}), title="Roles", description="Definition of the endpoints and of the authorized roles. This is automatically filled from role_file")
    role_file: str = Field(title="Role file", description="File location containing the roles")


class Settings(BaseModel, extra=Extra.allow):
    arlas_url_search: str = Field(title="ARLAS URL Search", description="ARLAS URL Search (ex http://arlas-server:9999/arlas/explore/{collection}/_search?f=id:eq:{item})")
    agate_prefix: str = Field(title="Agate endpoint prefix", description="Agate endpoint prefix")
    host: str = Field(title="Host", description="Agate service connection host")
    port: int = Field(title="Port", description="Agate service port")
    services: dict[str, Service] = Field({}, title="Services to protect", description="Dictionary of service name/definition. A service protects an endpoint that is exposing resources linked to an ARLAS Item. The service definition tells how to extract the collection name and the item id that are then used for checking with ARLAS whether the item is accessible or not.")
    urbac: URBAC = Field(title="URBAC definition", description="URL Role Based Access Control Definition. A user access an endpoint if one of his role is configured in the role configuration file for the requested endpoint (roles.yaml)")


class Configuration:
    settings: Settings = Field(title="Agate configuration", description="Configuration of ARLAS Gateway for Assets.")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
        with open(Configuration.settings.urbac.role_file, "r") as f:
            roles = yaml.safe_load(f)
            Configuration.settings.urbac.roles = Roles.model_validate(roles)
