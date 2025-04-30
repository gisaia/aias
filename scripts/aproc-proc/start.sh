#!/bin/sh
. aproc/bin/activate
celery -A aproc.core.processes.processes:APROC_CELERY_APP worker -E -c 1 -n worker@%h $*
