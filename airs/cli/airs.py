import os

import typer
import uvicorn
from fastapi import FastAPI

from airs.core.settings import Configuration
from airs.rest.services import ROUTER
from common.exception_handler import EXCEPTION_HANDLERS
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

cli = typer.Typer()
AIRS_HOST = os.getenv("AIRS_HOST", "127.0.0.1")
AIRS_PORT = os.getenv("AIRS_PORT", "8000")
AIRS_PREFIX = os.getenv("AIRS_PREFIX", "/arlas/airs")
AIRS_CORS = os.getenv("AIRS_CORS", "*")


@cli.command(help="Start the ARLAS Item Registration Service.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file"),
        host: str = typer.Argument(default=AIRS_HOST, help="host"),
        port: int = typer.Argument(default=AIRS_PORT, help="port")):
    Configuration.init(configuration_file=configuration_file)
    api = FastAPI(version='0.0', title='ARLAS Item Product Registration Service',
                  description='ARLAS Item Registration Service API',
                  middleware=[
                    Middleware(CORSMiddleware, allow_origins=AIRS_CORS.split(","))
                  ])
    api.include_router(ROUTER, prefix=AIRS_PREFIX)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)
    uvicorn.run(api, host=host, port=port)


if __name__ == "__main__":
    cli()
