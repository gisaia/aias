import os

import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from aproc.service.aproc_services import AprocServices
from aias_common.rest.exception_handler import EXCEPTION_HANDLERS
from aias_common.rest.healthcheck import ROUTER as HEALTHCHECK
from aproc.service.ogc_processes_api import ROUTER

cli = typer.Typer()
APROC_HOST = os.getenv("APROC_HOST", "127.0.0.1")
APROC_PORT = os.getenv("APROC_PORT", "8001")
APROC_PREFIX = os.getenv("APROC_PREFIX", "/arlas/aproc")
APROC_CORS_ORIGINS = os.getenv("APROC_CORS_ORIGINS", "*")
APROC_CORS_METHODS = os.getenv("APROC_CORS_METHODS", "*")
APROC_CORS_HEADERS = os.getenv("APROC_CORS_HEADERS", "*")
AIAS_VERSION = os.getenv("AIAS_VERSION", "0.0")


@cli.command(help="Start the ARLAS Processing Service.")
def run(
        host: str = typer.Argument(default=APROC_HOST, help="host"),
        port: int = typer.Argument(default=APROC_PORT, help="port")):
    api = FastAPI(version=AIAS_VERSION, title='ARLAS Processes',
                  description='ARLAS Processes',
                  middleware=[Middleware(CORSMiddleware, allow_origins=APROC_CORS_ORIGINS.split(","),
                                         allow_methods=APROC_CORS_METHODS.split(","),
                                         allow_headers=APROC_CORS_HEADERS.split(","))
                              ])
    api.include_router(ROUTER, prefix=APROC_PREFIX)
    api.include_router(HEALTHCHECK, prefix=APROC_PREFIX)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)

    AprocServices.init()
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    cli()
