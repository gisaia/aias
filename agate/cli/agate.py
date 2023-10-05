import os

import typer
import uvicorn
from fastapi import FastAPI

from agate.rest.service import ROUTER
from agate.settings import Configuration
from common.exception_handler import EXCEPTION_HANDLERS

cli = typer.Typer()

@cli.command(help="Start the ARLAS Item Registration Service.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file")):
    api = FastAPI(version='0.0', title='ARLAS ',
                  description='ARLAS Asset Gateway',
                  )
    Configuration.init(configuration_file)
    api.include_router(ROUTER, prefix=Configuration.settings.agate_prefix)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)
    uvicorn.run(api, host=Configuration.settings.host, port=Configuration.settings.port)

if __name__ == "__main__":
    cli()
