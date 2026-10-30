#!/usr/bin/env bash
set -Eeuo pipefail

CELERY_APP="${CELERY_APP:-aproc.core.healthcheck:HEALTH_CELERY_APP}"
DESTINATION="${CELERY_WORKER_NAME:-worker@${HOSTNAME}}"
TIMEOUT="${CELERY_HEALTHCHECK_TIMEOUT:-5}"

if celery -A "$CELERY_APP" inspect ping \
    --destination "$DESTINATION" \
    --timeout "$TIMEOUT" \
    >/dev/null 2>&1; then
    exit 0
fi
echo "Celery worker health check failed" >&2
exit 1