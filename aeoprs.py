import json
import logging
from datetime import datetime as Datetime
from pathlib import Path

import typer
import uvicorn
from fastapi import Body, FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from aeoprs.core.settings import Configuration
from aeoprs.logger import CustomLogger as Logger
from aeoprs.rest.services import api

cli = typer.Typer()
LOGGER_CONFIG_FILE = "conf/logging.json"

@cli.command(help="Start the ARLAS Earth Observation Product Registration Service.")
def run(
    configuration_file: str = typer.Argument(..., help="Configuration file"),
    host: str = typer.Argument(default="127.0.0.1", help="host"),
    port: int = typer.Argument(default=8000,help="port")
    ):
    Configuration.init(configuration_file=configuration_file)
    uvicorn.run(api, host=host, port=port)

if __name__ == "__main__":
    with open(LOGGER_CONFIG_FILE, "r") as f:
        Logger.register_logger(json.load(f))
    cli()
