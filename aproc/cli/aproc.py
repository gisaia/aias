import os

import typer
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware import Middleware

from aproc.service.aproc_services import AprocServices
from common.exception_handler import EXCEPTION_HANDLERS
from aproc.service.ogc_processes_api import ROUTER

cli = typer.Typer()
APROC_HOST = os.getenv("APROC_HOST", "127.0.0.1")
APROC_PORT = os.getenv("APROC_PORT", "8001")
APROC_PREFIX = os.getenv("APROC_PREFIX", "/arlas/aproc")
APROC_CORS = os.getenv("APROC_CORS", "*")


@cli.command(help="Start the ARLAS Processing Service.")
def run(
        host: str = typer.Argument(default=APROC_HOST, help="host"),
        port: int = typer.Argument(default=APROC_PORT, help="port")
        ):
    app = FastAPI(version='0.0', title='ARLAS Processes',
                  description='ARLAS Processes',
                  middleware=[
                    Middleware(CORSMiddleware, allow_origins=APROC_CORS.split(","))
                  ])
    app.include_router(ROUTER, prefix=APROC_PREFIX)
    for eh in EXCEPTION_HANDLERS:
        app.add_exception_handler(eh.exception, eh.handler)

    AprocServices.init()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    cli()
