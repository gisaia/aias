import os

import typer
import uvicorn
from fastapi import FastAPI

from airs.core.settings import Configuration
from airs.rest.services import ROUTER

cli = typer.Typer()
AIRS_HOST = os.getenv("AIRS_HOST", "127.0.0.1")
AIRS_PORT = os.getenv("AIRS_PORT", "8000")
AIRS_PREFIX = os.getenv("AIRS_PREFIX", "/arlas/airs")


@cli.command(help="Start the ARLAS Item Registration Service.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file"),
        host: str = typer.Argument(default=AIRS_HOST, help="host"),
        port: int = typer.Argument(default=AIRS_PORT, help="port")):
    Configuration.init(configuration_file=configuration_file)
    api = FastAPI(version='0.0', title='ARLAS Item Product Registration Service',
                  description='ARLAS Item Registration Service API',
                  )
    api.include_router(ROUTER, prefix=AIRS_PREFIX)
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    cli()
