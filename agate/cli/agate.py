import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware
import os

from agate.rest.service import ROUTER
from agate.settings import Configuration
from common.exception_handler import EXCEPTION_HANDLERS

cli = typer.Typer()
AGATE_CORS = os.getenv("AGATE_CORS", "*")


@cli.command(help="Start the ARLAS Asset Gateway.")
def run(configuration_file: str = typer.Argument(..., help="Configuration file")):
    api = FastAPI(version='0.0', title='ARLAS Asset Gateway',
                  description='ARLAS Asset Gateway API',
                  middleware=[
                    Middleware(CORSMiddleware, allow_origins=AGATE_CORS.split(","))
                  ])
    Configuration.init(configuration_file)
    api.include_router(ROUTER, prefix=Configuration.settings.agate_prefix)
    for eh in EXCEPTION_HANDLERS:
        api.add_exception_handler(eh.exception, eh.handler)
    uvicorn.run(api, host=Configuration.settings.host, port=Configuration.settings.port)


if __name__ == "__main__":
    cli()
