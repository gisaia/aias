import os

import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

from aproc.service.aproc_services import AprocServices
from aproc.service.ogc_processes_api import ROUTER
from common.exception_handler import EXCEPTION_HANDLERS
from common.healthcheck import ROUTER as HEALTHCHECK

cli = typer.Typer()
APROC_HOST = os.getenv("APROC_HOST", "127.0.0.1")
APROC_PORT = os.getenv("APROC_PORT", "8001")
APROC_PREFIX = os.getenv("APROC_PREFIX", "/arlas/aproc")
APROC_CORS_ORIGINS = os.getenv("APROC_CORS_ORIGINS", "*")
APROC_CORS_METHODS = os.getenv("APROC_CORS_METHODS", "*")
APROC_CORS_HEADERS = os.getenv("APROC_CORS_HEADERS", "*")


@cli.command(help="Start the ARLAS Processing Service.")
def run(
        host: str = typer.Argument(default=APROC_HOST, help="host"),
        port: int = typer.Argument(default=APROC_PORT, help="port")
        ):
    api = FastAPI(version='0.0', title='ARLAS Processes',
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
