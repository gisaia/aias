import json
import os

import typer
import uvicorn
from fastapi import FastAPI

from aproc.service.aproc_services import AprocServices
from aproc.service.exception_handler import EXCEPTION_HANDLERS
from aproc.service.ogc_processes_api import ROUTER
from common.logger import CustomLogger as Logger

cli = typer.Typer()
LOGGER_CONFIG_FILE = "conf/logging.json"
APROC_HOST = os.getenv("APROC_HOST", "127.0.0.1")
APROC_PORT = os.getenv("APROC_PORT", "8001")


@cli.command(help="Start the ARLAS Processing Service.")
def run(
        host: str = typer.Argument(default=APROC_HOST, help="host"),
        port: int = typer.Argument(default=APROC_PORT, help="port")
        ):
    app = FastAPI()
    app.include_router(ROUTER)
    for eh in EXCEPTION_HANDLERS:
        app.add_exception_handler(eh.exception, eh.handler)

    AprocServices.init()
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    with open(LOGGER_CONFIG_FILE, "r") as f:
        Logger.register_logger(json.load(f))
    cli()
