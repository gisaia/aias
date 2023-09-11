import json
import os

import typer
import uvicorn

from aeoprs.core.settings import Configuration
from aeoprs.logger import CustomLogger as Logger
from aeoprs.rest.services import api

cli = typer.Typer()
LOGGER_CONFIG_FILE = "conf/logging.json"
AEOPRS_HOST=os.getenv("AEOPRS_HOST","127.0.0.1")
AEOPRS_PORT=os.getenv("AEOPRS_PORT", "8000")

@cli.command(help="Start the ARLAS Earth Observation Product Registration Service.")
def run(
    configuration_file: str = typer.Argument(..., help="Configuration file"),
    host: str = typer.Argument(default=AEOPRS_HOST, help="host"),
    port: int = typer.Argument(default=AEOPRS_PORT,help="port")
    ):
    Configuration.init(configuration_file=configuration_file)
    uvicorn.run(api, host=host, port=port)

if __name__ == "__main__":
    with open(LOGGER_CONFIG_FILE, "r") as f:
        Logger.register_logger(json.load(f))
    cli()
