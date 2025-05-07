import os

import typer
import uvicorn
from fastapi import FastAPI

from airs.core.settings import Configuration
from airs.rest.services import ROUTER
from aias_common.rest.exception_handler import EXCEPTION_HANDLERS
from aias_common.rest.healthcheck import ROUTER as HEALTHCHECK
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

cli = typer.Typer()
AIRS_HOST = os.getenv("AIRS_HOST", "127.0.0.1")
AIRS_PORT = os.getenv("AIRS_PORT", "8000")
AIRS_PREFIX = os.getenv("AIRS_PREFIX", "/arlas/airs")
AIRS_CORS_ORIGINS = os.getenv("AIRS_CORS_ORIGINS", "*")
AIRS_CORS_METHODS = os.getenv("AIRS_CORS_METHODS", "*")
AIRS_CORS_HEADERS = os.getenv("AIRS_CORS_HEADERS", "*")
AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")


@cli.command(help="Start the ARLAS Item Registration Service.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file"),
        host: str = typer.Argument(default=AIRS_HOST, help="host"),
        port: int = typer.Argument(default=AIRS_PORT, help="port")):
    Configuration.init(configuration_file=configuration_file)
    api = FastAPI(version=AIAS_VERSION, title='ARLAS Item Product Registration Service',
                  description='ARLAS Item Registration Service API',
                  middleware=[Middleware(CORSMiddleware, allow_origins=AIRS_CORS_ORIGINS.split(","),
                                         allow_methods=AIRS_CORS_ORIGINS.split(","),
                                         allow_headers=AIRS_CORS_HEADERS.split(","))
                              ])
    api.include_router(ROUTER, prefix=AIRS_PREFIX)
    api.include_router(HEALTHCHECK, prefix=AIRS_PREFIX)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    cli()
