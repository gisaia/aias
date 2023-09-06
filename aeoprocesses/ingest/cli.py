from aeoprocesses.settings import Configuration
from aeoprocesses.ingest.drivers.drivers import Drivers
from aeoprocesses.ingest.drivers.exceptions import DriverException
import aeoprocesses.ingest.proc as proc
from celery import states
from celery.result import AsyncResult
from pydantic import BaseModel, Field
import typer
from aeoprocesses.ingest.ingest_services import ProcServices

cli = typer.Typer()

@cli.command(help="Ingest one archive")
def ingest(
    configuration_file: str = typer.Argument(..., help="Configuration file"),
    archive: str = typer.Argument(..., help="URL or path to the archive"),
    ):
    ProcServices.init(configuration_file=configuration_file)
    ProcServices.sync_register(archive)

if __name__ == "__main__":
    cli()
