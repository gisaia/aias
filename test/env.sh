export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test
export APROC_CONFIGURATION_FILE=`pwd`/conf/aproc.yaml
export APROC_ENDPOINT=http://localhost:8001/arlas/aproc
export ROOT_DIRECTORY=`pwd`/test/inputs

# for aproc to contact airs
export AIRS_URL=http://airs-server:8000/arlas/airs

export AIRS_ARLAS_COLLECTION_NAME=tests
export AIRS_ARLAS_URL=http://localhost:81/server
export AIRS_INDEX_ENDPOINT_URL=http://elasticsearch:9200
export AIRS_INDEX_COLLECTION_PREFIX=airs
export AIRS_S3_BUCKET=airstest
export AIRS_S3_ACCESS_KEY_ID=airs
export AIRS_S3_SECRET_ACCESS_KEY=airssecret
export AIRS_S3_TIER=Standard
export AIRS_S3_PLATFORM=minio
export AIRS_S3_ENDPOINT_URL=http://minio:9000
export AIRS_S3_ASSET_HTTP_ENDPOINT_URL=http://minio:9000/{}/{}
export AIRS_MAPPING_URL=/app/conf/mapping.json
export AIRS_COLLECTION_URL=/app/conf/collection.json

export ARLAS_SMTP_ACTIVATED=true
export ARLAS_SMTP_HOST=smtp4dev
export ARLAS_SMTP_PORT=25
export ARLAS_SMTP_USERNAME=whatever
export ARLAS_SMTP_PASSWORD=whatever
export ARLAS_SMTP_FROM=noreply@arlas.io
export APROC_DOWNLOAD_OUTBOX_DIR=/outbox
export APROC_DOWNLOAD_ADMIN_EMAILS="admin@the.boss,someone.else@the.boss"

export APROC_DOWNLOAD_CONTENT_USER="Download done."
export APROC_DOWNLOAD_SUBJECT_USER="Download done."

export APROC_DOWNLOAD_CONTENT_ERROR="Download failed."
export APROC_DOWNLOAD_SUBJECT_ERROR="Download failed."

export APROC_DOWNLOAD_CONTENT_ADMIN="Download done."
export APROC_DOWNLOAD_SUBJECT_ADMIN="Download done."

#TODO add a function to identify the right platform
export PLATFORM='amd64'