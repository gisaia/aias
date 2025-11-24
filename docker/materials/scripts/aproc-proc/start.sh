#!/bin/bash
set -o errexit

DEFAULT_QUEUE="aproc_task_queue"

if [[ ${QUEUE_NAMES} ]]; then
    echo "Starting worker for queues: ${QUEUE_NAMES}"
else
    QUEUE_NAMES=$DEFAULT_QUEUE
    echo "Starting worker for default queue: $QUEUE_NAMES"
fi

. aproc/bin/activate
celery -A aproc.core.processes.processes:APROC_CELERY_APP worker -Q ${QUEUE_NAMES} -E -c 1 -n worker@%h $*
