import typer
from aproc.ingest.ingest_services import ProcServices

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
