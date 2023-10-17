import os

import typer
import uvicorn
from fastapi import FastAPI

from common.exception_handler import EXCEPTION_HANDLERS
from extensions.aproc.proc.ingest.drivers.drivers import Drivers
from fam.core.settings import Configuration
from fam.rest.services import ROUTER

cli = typer.Typer()
FAM_HOST = os.getenv("FAM_HOST", "0.0.0.0")
FAM_PORT = os.getenv("FAM_PORT", "8005")
FAM_PREFIX = os.getenv("FAM_PREFIX", "/arlas/fam")


@cli.command(help="Start the File and Archive Management Service.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file"),
        host: str = typer.Argument(default=FAM_HOST, help="host"),
        port: int = typer.Argument(default=FAM_PORT, help="port")):
    Configuration.init(configuration_file=configuration_file)
    Drivers.init(configuration_file=Configuration.settings.driver_configuration_file)
    api = FastAPI(version='0.0', title='ARLAS File and Archive Management Service',
                  description='ARLAS File and Archive Management API',
                  )
    api.include_router(ROUTER, prefix=FAM_PREFIX)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)
    uvicorn.run(api, host=host, port=port)

if __name__ == "__main__":
    cli()
