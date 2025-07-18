#!/bin/sh
set -o errexit -o pipefail
. aproc/bin/activate
celery inspect ping --destination worker@$HOSTNAME
