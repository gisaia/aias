from aeoprocesses.settings import Configuration
from aeoprocesses.ingest.drivers.drivers import Drivers
from aeoprocesses.ingest.drivers.exceptions import DriverException
import aeoprocesses.ingest.proc as proc
from celery import states
from celery.result import AsyncResult
from pydantic import BaseModel, Field
import typer

class TaskState(BaseModel):
    task_id                : str           | None = Field(default=None, title="The task's id")
    state                  : str           | None = Field(default=None, title="The task's state")
    info                   : dict           | None = Field(default=None, title="The task's information")

class ProcServices:

    @staticmethod
    def init(configuration_file:str):
        Configuration.init(configuration_file=configuration_file)
        Drivers.init()

    @staticmethod
    def async_register(url:str)->str:
        """Launch asynchronously the ingestion of the archive pointed by the url

        Args:
            url (str): url pointing at the archive

        Raises:
            DriverException: exception raised if no driver found

        Returns:
            str: the task id of the job
        """
        driver=Drivers.solve(url)
        if driver is not None:
            job:AsyncResult=proc.ingest.s(driver.name, url, "main_catalog", "theia").delay()
        else:
            raise DriverException("Driver not found for {}".format(url))
        return job.id

    @staticmethod
    def sync_register(url:str)->str:
        """Launch synchronously the ingestion of the archive pointed by the url

        Args:
            url (str): url pointing at the archive

        Raises:
            DriverException: exception raised if no driver found

        Returns:
            str: a dictionary containing three keys: action, state and item. Item points at the aeoprs registered item.

        """
        driver=Drivers.solve(url)
        if driver is not None:
            return proc.ingest(driver.name, url, "main_catalog", "theia")
        else:
            raise DriverException("Driver not found for {}".format(url))

    @staticmethod
    def get_state(task_id:str):
        """The state of the task

        Args:
            task_id (str): task id

        Returns:
            _type_: state of the task. See celery.states
        """             
        res = AsyncResult(task_id,app=proc.app)
        return TaskState(task_id=task_id, state=res.status, info=res.info)

