
import re

import requests
from fastapi import APIRouter, Request, status
from fastapi.responses import Response

from agate.logger import Logger
from agate.settings import Configuration

LOGGER = Logger.logger
ROUTER = APIRouter()


@ROUTER.get("/authorization")
async def path(request: Request):
    requested_path = request.headers[Configuration.settings.url_header]
    LOGGER.debug("Incoming URI: {}".format(requested_path))
    if not not Configuration.settings.url_header_prefix:
        requested_path = requested_path.removeprefix(Configuration.settings.url_header_prefix)
    LOGGER.debug("URI for matching: {}".format(requested_path))
    patterns = Configuration.settings.url_patterns
    public_patterns = Configuration.settings.public_url_patterns
    for pattern in public_patterns:
        LOGGER.debug("test against public pattern {}".format(pattern))
        matches = re.finditer(pattern=pattern, string=requested_path)
        for match in matches:
            return Response(status_code=status.HTTP_202_ACCEPTED)
    for pattern in patterns:
        LOGGER.debug("test against {}".format(pattern))
        matches = re.finditer(pattern=pattern, string=requested_path)
        for match in matches:
            if match.start() == 0:
                LOGGER.debug("{} matches {}".format(requested_path, pattern))
                try:
                    r = requests.get(Configuration.settings.arlas_url_search.format(collection=match.group("collection"), item=match.group("item")), headers=request.headers)
                    if r.ok:
                        response = r.json()
                        if response["hits"] is not None and len(response["hits"]) > 0:
                            LOGGER.debug("ARLAS returned {} result(s) for {}".format(len(response["hits"]), requested_path))
                            return Response(status_code=status.HTTP_202_ACCEPTED)
                        else:
                            LOGGER.debug("ARLAS returned zero results for {}".format(requested_path))
                    else:
                        LOGGER.error("ARLAS failed to answer {}: {}".format(str(r.status_code), str(r.content)))
                        return Response(status_code=r.status_code)
                except Exception as e:
                    LOGGER.exception(e)
                    return Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                LOGGER.debug("Match not starting at the begining.")
    return Response(status_code=status.HTTP_403_FORBIDDEN)
