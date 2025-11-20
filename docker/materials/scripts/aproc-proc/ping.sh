#!/bin/bash
set -o errexit -o pipefail

EXTRA_OPT=""
if [ -z "$BROKER" ]
then
    echo "Using default broker"
else
    echo "Using provided broker $BROKER"
    EXTRA_OPT="-b "`echo $BROKER | sed 's/pyamqp:\/\//amqp:\/\//'`
fi

. aproc/bin/activate
celery $EXTRA_OPT inspect ping --destination worker@$HOSTNAME
