from aproc.core.settings import Configuration
from celery import Celery
from celery.utils.log import get_task_logger
import os

LOGGER = get_task_logger(__name__)
LOGGER.debug(True)
LOGGER.propagate = True
Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))

APROC_CELERY_APP = Celery(name='aproc', broker=Configuration.settings.celery_broker_url, backend=Configuration.settings.celery_result_backend)

# TODO : register dynamically tasks based on configuration
from aproc.proc.ingest.task import ingest
APROC_CELERY_APP.task(ingest)
