import os
from aproc.core.settings import Configuration

from celery import Celery
Configuration.init(os.environ.get("APROC_CONFIGURATION_FILE"))

HEALTH_CELERY_APP = Celery(
    "aproc-healthcheck",
    broker=Configuration.settings.celery_broker_url,
)