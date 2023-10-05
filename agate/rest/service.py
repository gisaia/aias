
import re

import requests
from fastapi import APIRouter, Request, status
from fastapi.responses import Response

from agate.logger import Logger
from agate.settings import Configuration

LOGGER = Logger.logger

ROUTER = APIRouter()


@ROUTER.get("/{path:path}")
async def path(request: Request, path: str):
    requested_path = ("/"+str(request.url).removeprefix(str(request.base_url))).removeprefix(Configuration.settings.agate_prefix)
    LOGGER.debug("Incopming request: {}".format(requested_path))
    patterns = Configuration.settings.url_patterns
    for pattern in patterns:
        LOGGER.debug("test against {}".format(pattern))
        matches = re.finditer(pattern=pattern, string=requested_path)
        for match in matches:
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
    return Response(status_code=status.HTTP_403_FORBIDDEN)
