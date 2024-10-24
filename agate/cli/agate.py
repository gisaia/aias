import os

import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from agate.rest.service import ROUTER
from agate.settings import Configuration
from common.exception_handler import EXCEPTION_HANDLERS
from common.healthcheck import ROUTER as HEALTHCHECK

cli = typer.Typer()
AGATE_CORS_ORIGINS = os.getenv("AGATE_CORS_ORIGINS", "*")
AGATE_CORS_METHODS = os.getenv("AGATE_CORS_METHODS", "*")
AGATE_CORS_HEADERS = os.getenv("AGATE_CORS_HEADERS", "*")


@cli.command(help="Start the ARLAS Asset Gateway.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file")):
    api = FastAPI(version='0.0', title='ARLAS Asset Gateway',
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
    uvicorn.run(api, host=Configuration.settings.host, port=Configuration.settings.port)


if __name__ == "__main__":
    cli()
