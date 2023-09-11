import json
import os

import typer
import uvicorn

from airs.core.settings import Configuration
from airs.logger import CustomLogger as Logger
from airs.rest.services import api

cli = typer.Typer()
LOGGER_CONFIG_FILE = "conf/logging.json"
AIRS_HOST=os.getenv("AIRS_HOST","127.0.0.1")
AIRS_PORT=os.getenv("AIRS_PORT", "8000")

@cli.command(help="Start the ARLAS Item Registration Service.")
def run(
    configuration_file: str = typer.Argument(..., help="Configuration file"),
    host: str = typer.Argument(default=AIRS_HOST, help="host"),
    port: int = typer.Argument(default=AIRS_PORT,help="port")
    ):
    Configuration.init(configuration_file=configuration_file)
    uvicorn.run(api, host=host, port=port)

if __name__ == "__main__":
    with open(LOGGER_CONFIG_FILE, "r") as f:
        Logger.register_logger(json.load(f))
    cli()
