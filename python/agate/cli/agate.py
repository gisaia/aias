import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import os
from agate.logger import Logger

from agate.rest.key_ring import KeyRing
from agate.rest.service import ROUTER
from agate.settings import Configuration
from aias_common.rest.exception_handler import EXCEPTION_HANDLERS
from aias_common.rest.healthcheck import ROUTER as HEALTHCHECK
cli = typer.Typer()
AGATE_CORS_ORIGINS = os.getenv("AGATE_CORS_ORIGINS", "*")
AGATE_CORS_METHODS = os.getenv("AGATE_CORS_METHODS", "*")
AGATE_CORS_HEADERS = os.getenv("AGATE_CORS_HEADERS", "*")
AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")
LOGGER = Logger.logger


@cli.command(help="Start the ARLAS Asset Gateway.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file")):
    api = FastAPI(version=AIAS_VERSION, title='ARLAS Asset Gateway',
                  description='ARLAS Asset Gateway API',
                  middleware=[Middleware(CORSMiddleware, allow_origins=AGATE_CORS_ORIGINS.split(","),
                                         allow_methods=AGATE_CORS_METHODS.split(","),
                                         allow_headers=AGATE_CORS_HEADERS.split(","))
                              ])
    Configuration.init(configuration_file)
    api.include_router(ROUTER, prefix=Configuration.settings.agate_prefix)
    api.include_router(HEALTHCHECK, prefix=Configuration.settings.agate_prefix)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)
    if not Configuration.settings.verify_jwt:
        LOGGER.warning("JWT verification is disabled, this should never be the case in production.")
    else:
        if Configuration.settings.open_id_provider:
            if not Configuration.settings.verify_ssl:
                LOGGER.warning("SSL verification is disabled, this should never be the case in production.")
            KeyRing.load_from_openid_configuration(Configuration.settings.open_id_provider, Configuration.settings.verify_ssl)
        else:
            raise Exception("JWT verification is enabled but no Open ID Provider provided, JWT won't be accepted.")
    uvicorn.run(api, host=Configuration.settings.host, port=Configuration.settings.port)


if __name__ == "__main__":
    cli()
