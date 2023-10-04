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

export APROC_DOWNLOAD_SUBJECT_USER="\"ARLAS Services: Your download of {collection}/{item_id}/{asset_name} is available.\""
export APROC_DOWNLOAD_CONTENT_USER="\"ARLAS Services: Dear {arlas-user-email}. Your download of {collection}/{item_id}/{asset_name} is available for projection {target_projection} ({target_format}).ARLAS Services.\""

export APROC_DOWNLOAD_REQUEST_SUBJECT_USER="\"ARLAS Services: Thank you for your download request (({collection}/{item_id}/{asset_name}).\""
export APROC_DOWNLOAD_REQUEST_CONTENT_USER="\"ARLAS Services: Dear {arlas-user-email}. Your download request for {collection}/{item_id}/{asset_name} with projection {target_projection} ({target_format}) will shortly be taken into account. ARLAS Services.\""

export APROC_DOWNLOAD_SUBJECT_ERROR="\"ARLAS Services: ERROR: The download of {collection}/{item_id}/{asset_name} failed.\""
export APROC_DOWNLOAD_CONTENT_ERROR="\"ARLAS Services: The download of {collection}/{item_id}/{asset_name} failed ({error}).\""

export APROC_DOWNLOAD_SUBJECT_ADMIN="\"ARLAS Services: The download of {collection}/{item_id}/{asset_name} for {arlas-user-email} is available.\""
export APROC_DOWNLOAD_CONTENT_ADMIN="\"ARLAS Services: The download of {collection}/{item_id}/{asset_name} for {arlas-user-email} is available in {target_directory} ({file_name}) for projection {target_projection} ({target_format}). ARLAS Services.\""

export APROC_DOWNLOAD_REQUEST_SUBJECT_ADMIN="\"ARLAS Services: {arlas-user-email} requested the download of {collection}/{item_id}/{asset_name}.\""
export APROC_DOWNLOAD_REQUEST_CONTENT_ADMIN="\"ARLAS Services: {arlas-user-email} requested the download of {collection}/{item_id}/{asset_name} for projection {target_projection} ({target_format}). ARLAS Services.\""

export APROC_EMAIL_PATH_PREFIX_ADD="Y://DISK1"
export APROC_PATH_TO_WINDOWS=true

export PLATFORM='amd64'