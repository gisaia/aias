from aproc.core.settings import Configuration
from celery.result import AsyncResult
from pydantic import BaseModel, Field
from aproc.core.aproc_celery_app import APROC_CELERY_APP


class TaskState(BaseModel):
    task_id: str | None = Field(default=None, title="The task's id")
    state: object | None = Field(default=None, title="The task's state")
    info: object | None = Field(default=None, title="The task's information")


class ProcServices:

    @staticmethod
    def init(configuration_file: str):
        Configuration.init(configuration_file=configuration_file)

    @staticmethod
    def async_register(url: str, collection, catalog) -> str:
        """Launch asynchronously the ingestion of the archive pointed by the url
        
        Args:
            url (str): url pointing at the archive

        Returns:
            str: the task id of the job
        """
        job: AsyncResult = APROC_CELERY_APP.send_task(name="ingest", args=[url, collection, catalog])
        return job.id

    @staticmethod
    def sync_register(url: str, collection, catalog) -> str:
        """Launch synchronously the ingestion of the archive pointed by the url

        Args:
            url (str): url pointing at the archive

        Raises:
            DriverException: exception raised if no driver found

        Returns:
            str: a dictionary containing three keys: action, state and item. Item points at the airs registered item.

        """
        from aproc.proc.ingest.task import ingest
        return ingest(url, collection, catalog)

    @staticmethod
    def get_state(task_id: str):
        """The state of the task

        Args:
            task_id (str): task id

        Returns:
            _type_: state of the task. See celery.states
        """             
        res = AsyncResult(task_id, app=APROC_CELERY_APP)
        return TaskState(task_id=task_id, state=res.status, info=res.info)

