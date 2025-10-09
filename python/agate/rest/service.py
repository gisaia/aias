
import re
from urllib import parse
from fastapi import APIRouter, Request, status
from fastapi.responses import Response

from agate.logger import Logger
from agate.rest.authorizations import Authorizations
from agate.settings import Configuration, ParamLocation, Service

LOGGER = Logger.logger
ROUTER = APIRouter()
MISSING_MSG = "{} missing"


@ROUTER.get("/url-role-based-authorization")
async def urbac(request: Request):
    LOGGER.debug(request.headers)

    authorization = request.headers.get(Configuration.settings.urbac.jwt_header)
    if not authorization:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, content=MISSING_MSG.format(Configuration.settings.urbac.jwt_header))

    request_path = request.headers.get(Configuration.settings.url_header)
    if not authorization:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, content=MISSING_MSG.format(Configuration.settings.url_header))

    request_method = request.headers.get(Configuration.settings.method_header)
    if not request_method:
        return Response(status_code=status.HTTP_401_UNAUTHORIZED, content=MISSING_MSG.format(Configuration.settings.method_header))
    LOGGER.debug("Incoming request: {} on {}".format(request_method, request_path))

    try:
        user_roles = Authorizations.get_user_roles(authorization)
    except Exception as e:
        msg = "Invalid authorization header value {}".format(e)
        LOGGER.error(msg)
        LOGGER.debug(authorization)
        return Response(status_code=status.HTTP_403_FORBIDDEN, content=msg)
    
    LOGGER.debug("User's roles {}".format(", ".join(user_roles)))
    for n, r in Configuration.settings.urbac.roles.technicalRoles.items():
        if n in user_roles:
            for p in r.permissions:
                components = p.split(":")
                if len(components) == 3:
                    role_type, url_pattern, verbs = components
                    if role_type == "r":
                        if request_method.lower() in verbs.lower().split(","):
                            matches = re.finditer(pattern=url_pattern, string=request_path)
                            for match in matches:
                                if match.start() == 0:
                                    LOGGER.debug("{} matches {}".format(request_path, url_pattern))
                                    return Response(status_code=status.HTTP_202_ACCEPTED)
                            LOGGER.debug("{} does not matches {}".format(request_path, url_pattern))
                else:
                    LOGGER.warning("unrecognized permission {}".format(p))
        else:
            LOGGER.debug("user hasn't role {}".format(n))
    return Response(status_code=status.HTTP_403_FORBIDDEN)


@ROUTER.get("/authorization/{service}")
async def authorization(request: Request, service: str):
    service_conf: Service = Configuration.settings.services.get(service)
    if not service_conf:
        msg = "Service {} not found".format(service)
        LOGGER.error(msg)
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=msg)

    requested_path: str = request.headers[Configuration.settings.url_header]
    LOGGER.debug("Incoming URI: {}".format(requested_path))
    
    if Authorizations.at_least_one_rule_match_on_path(service_conf.public, requested_path, arlas_control=False):
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        LOGGER.debug("No public rule matches {}".format(requested_path))

    headers: dict[str, str] = {}
    for h in Configuration.settings.headers_for_arlas:
        headers[h] = request.headers.get(h, "")
    if (not headers.get(service_conf.jwt_name, None)) and ParamLocation.query_params in service_conf.jwt_locations:
        try:
            v = parse.parse_qs(requested_path).get(service_conf.jwt_name, "")
            if len(v) > 0:
                headers[service_conf.jwt_name] = v[0]
            else:
                LOGGER.debug("Couldn't extract {} from {}".format(service_conf.jwt_name, requested_path))
        except:
            LOGGER.debug("Couldn't extract {} from {}".format(service_conf.jwt_name, requested_path))
    if Authorizations.at_least_one_rule_match_on_path(service_conf.private, requested_path, arlas_control=True, headers=headers):
        return Response(status_code=status.HTTP_202_ACCEPTED)
    else:
        LOGGER.debug("No private rule matches {}".format(requested_path))
    return Response(status_code=status.HTTP_403_FORBIDDEN)
