from enum import Enum
from pydantic import BaseModel, Extra, Field
from envyaml import EnvYAML
from agate.logger import Logger
from agate.roles_model import Roles
import yaml

LOGGER = Logger.get_logger()


class Rule(BaseModel, extra=Extra.allow):
    pattern: str = Field(title="Pattern", description="Regex pattern to match the URL part of interest in order to extract the collection name and the item id with the keywords '<collection>' and '<item>'. E.g. (?P<collection>[^/]+)/items/(?P<item>[^/]+)/assets/overview")
    part: str | None = Field(title="Part to target for the pattern matching", description="If undefined, then the pattern is matched against the path. Use query.{param}, where {param} is the parameter value, to use a query parameter. Use query.{param}.url.path|query if the param value is a url and that you want to target the path or query of that url.")


class ParamLocation(str, Enum):
    headers = "headers"
    query_params = "query_params"


class Service(BaseModel, extra=Extra.allow):
    public: list[Rule] = Field([], title="Rules for public resources", description="Access is allowed if one of the rule is matching the URL part of interest. No access control is done.")
    private: list[Rule] = Field([], title="Rules for controlled resources", description="Access is allowed if one of the rule is matching the URL part of interest and if the user has access to the corresponding ARLAS Item.")
    jwt_name: str = Field("authorization", title="JWT parameter name", description="The name of the parameter containing the JWT")
    jwt_locations: list[ParamLocation] = Field([ParamLocation.headers, ParamLocation.query_params], title="JWT location", description="The location in the request containing the JWT parameter")


class URBAC(BaseModel, extra=Extra.allow):
    roles: Roles = Field(default=Roles(technicalRoles={}), title="Roles", description="Definition of the endpoints and of the authorized roles. This is automatically filled from role_file")
    role_file: str = Field(title="Role file", description="File location containing the roles")
    verify_jwt: bool = Field(True, title="Verify JWT", description="Whether to verify the JWT signature. Should be True in production.")
    jwks_uri: str | None = Field("", title="jwks url", description="Must be provided for production.")
    verify_ssl: bool = Field(True, title="Verify SSL", description="Whether to verify SSL certificates when fetching the OpenID configuration and JWKS. Should be True in production.")
    jwt_audience: str = Field("", title="JWT Audience", description="Expected audience in the JWT. If not set, no audience verification is done.")
    jwt_header: str = Field("authorization", title="JWT header name", description="The name of the header parameter containing the JWT")


class Settings(BaseModel, extra=Extra.allow):
    method_header: str = Field("x-forwarded-method", title="Method header", description="The header containing the method")
    url_header: str = Field("X-Forwarded-Uri", title="URL Header", description="The header containing the requested URL")
    arlas_url_search: str = Field(title="ARLAS URL Search", description="ARLAS URL Search (ex http://arlas-server:9999/arlas/explore/{collection}/_search?f=id:eq:{item})")
    agate_prefix: str = Field(title="Agate endpoint prefix", description="Agate endpoint prefix")
    host: str = Field(title="Host", description="Agate service connection host")
    port: int = Field(title="Port", description="Agate service port")
    services: dict[str, Service] = Field({}, title="Services to protect", description="Dictionary of service name/definition. A service protects an endpoint that is exposing resources linked to an ARLAS Item. The service definition tells how to extract the collection name and the item id that are then used for checking with ARLAS whether the item is accessible or not.")
    urbac: URBAC = Field(title="URBAC definition", description="URL Role Based Access Control Definition. A user access an endpoint if one of his role is configured in the role configuration file for the requested endpoint (roles.yaml)")
    headers_for_arlas: list[str] = Field(["authorization", "arlas-org-filter"], title="Headers forwarded to arlas", description="The header to be forwarded to ARLAS")


class Configuration:
    settings: Settings = Field(title="Agate configuration", description="Configuration of ARLAS Gateway for Assets.")

    @staticmethod
    def init(configuration_file: str):
        envyaml = EnvYAML(configuration_file, strict=False)
        Configuration.settings = Settings.model_validate(envyaml.export())
        with open(Configuration.settings.urbac.role_file, "r") as f:
            roles = yaml.safe_load(f)
            Configuration.settings.urbac.roles = Roles.model_validate(roles)
