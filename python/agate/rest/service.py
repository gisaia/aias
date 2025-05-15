
import re

import requests
from fastapi import APIRouter, Request, status
from fastapi.responses import Response

from agate.logger import Logger
from agate.settings import Configuration, Service
from urllib import parse

LOGGER = Logger.logger
ROUTER = APIRouter()


@ROUTER.get("/authorization/{service}")
async def path(request: Request, service: str):
    service: Service = Configuration.settings.services.get(service)
    if not service:
        msg = "Service {} not found".format(service)
        LOGGER.error(msg)
        return Response(status_code=status.HTTP_404_NOT_FOUND, content=msg)
    requested_path = request.headers[service.url_header]
    LOGGER.debug("Incoming URI: {}".format(requested_path))
    if service.pattern_target:
        LOGGER.debug("Using {} for computing the target".format(service.pattern_target))
        if service.pattern_target.startswith("query."):
            param_name = service.pattern_target.split(".")[1]
            LOGGER.debug("Using query parameter {} as target".format(param_name))
            query = parse.urlparse(requested_path).query
            param = parse.parse_qs(query).get(param_name)
            if param is None or len(param) < 1:
                msg = "Parameter {} not found in query {} for service {}".format(param_name, query, service)
                LOGGER.error(msg)
                return Response(status_code=status.HTTP_404_NOT_FOUND, content=msg)
            else:
                param = param[0]
            LOGGER.debug("{}={}".format(param_name, param))
            if service.pattern_target.endswith(".path") or service.pattern_target.endswith(".query"):
                url: parse.ParseResult = parse.urlparse(param)
                if service.pattern_target.endswith(".url.path"):
                    LOGGER.debug("Using path of url {} as target".format(param))
                    target = url.path
                elif service.pattern_target.endswith(".url.query"):
                    LOGGER.debug("Using query of url {} as target".format(param))
                    target = url.query
            else:
                LOGGER.debug("Using query parameter {} as target".format(param_name))
                target = parse.urlparse(requested_path).query
        else:
            msg = "Invalid configuration '{}' for pattern_target of {}".format(service.pattern_target, service)
            LOGGER.error(msg)
            return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content=msg)
    else:
        LOGGER.debug("Using path as target")
        target = requested_path
    if service.url_header_prefix:
        target = target.removeprefix(service.url_header_prefix)
    LOGGER.debug("Pattern matching on: {}".format(target))
    patterns = service.url_patterns
    public_patterns = service.public_url_patterns
    if public_patterns:
        for pattern in public_patterns:
            LOGGER.debug("test against public pattern {}".format(pattern))
            matches = re.finditer(pattern=pattern, string=target)
            for match in matches:
                if match.start() == 0:
                    return Response(status_code=status.HTTP_202_ACCEPTED)
    if not patterns:
        return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content="Invalid configuration: not pattern configured for {}".format(service))
    for pattern in patterns:
        LOGGER.debug("test against {}".format(pattern))
        matches = re.finditer(pattern=pattern, string=target)
        for match in matches:
            if match.start() == 0:
                LOGGER.debug("{} matches {}".format(target, pattern))
                try:
                    r = requests.get(Configuration.settings.arlas_url_search.format(collection=match.group("collection"), item=match.group("item")), headers={"authorization": request.headers.get("authorization"), "arlas-org-filter": request.headers.get("arlas-org-filter")})
                    if r.ok:
                        response = r.json()
                        if response["hits"] is not None and len(response["hits"]) > 0:
                            LOGGER.debug("ARLAS returned {} result(s) for {}".format(len(response["hits"]), target))
                            return Response(status_code=status.HTTP_202_ACCEPTED)
                        else:
                            LOGGER.debug("ARLAS returned zero results for {}".format(target))
                    else:
                        LOGGER.error("ARLAS failed to answer {}: {}".format(str(r.status_code), str(r.content)))
                        return Response(status_code=r.status_code)
                except Exception as e:
                    LOGGER.exception(e)
                    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                LOGGER.debug("Match not starting at the begining.")
    return Response(status_code=status.HTTP_403_FORBIDDEN)
