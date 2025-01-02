import os

import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from common.healthcheck import ROUTER as HEALTHCHECK
from extensions.aproc.proc.drivers.driver_manager import DriverManager
from extensions.aproc.proc.ingest.settings import Configuration as IngestConfiguration
from fam.core.settings import Configuration
from fam.rest.services import ROUTER

cli = typer.Typer()
FAM_HOST = os.getenv("FAM_HOST", "0.0.0.0")
FAM_PORT = os.getenv("FAM_PORT", "8005")
FAM_PREFIX = os.getenv("FAM_PREFIX", "/arlas/fam")
FAM_CORS_ORIGINS = os.getenv("FAM_CORS_ORIGINS", "*")
FAM_CORS_METHODS = os.getenv("FAM_CORS_METHODS", "*")
FAM_CORS_HEADERS = os.getenv("FAM_CORS_HEADERS", "*")


@cli.command(help="Start the File and Archive Management Service.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file"),
        host: str = typer.Argument(default=FAM_HOST, help="host"),
        port: int = typer.Argument(default=FAM_PORT, help="port")):

    Configuration.init(configuration_file=configuration_file)
    IngestConfiguration.init(configuration_file=Configuration.settings.driver_configuration_file)
    DriverManager.init("ingest", IngestConfiguration.settings.drivers)
    api = FastAPI(version='0.0', title='ARLAS File and Archive Management Service',
                  description='ARLAS File and Archive Management API',
                  middleware=[Middleware(CORSMiddleware, allow_origins=FAM_CORS_ORIGINS.split(","),
                                         allow_methods=FAM_CORS_METHODS.split(","),
                                         allow_headers=FAM_CORS_HEADERS.split(","))
                              ])
    api.include_router(ROUTER, prefix=FAM_PREFIX)
    api.include_router(HEALTHCHECK, prefix=FAM_PREFIX)
#    for eh in EXCEPTION_HANDLERS:
#        api.add_exception_handler(eh.exception, eh.handler)
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    cli()
