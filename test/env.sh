export PYTHONPATH=`pwd`:`pwd`/extensions:`pwd`/test
export APROC_CONFIGURATION_FILE=`pwd`/conf/aproc.yaml
export APROC_ENDPOINT=http://localhost:8001/arlas/aproc
export ROOT_DIRECTORY=`pwd`/test/inputs

# AIRS
export AIRS_CORS_ORIGINS="*"
export AIRS_CORS_METHODS="*"
export AIRS_CORS_HEADERS="*"
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
export ARLASEO_MAPPING_URL=/app/conf/mapping.json
export AIRS_COLLECTION_URL=/app/conf/collection.json
export AIRS_LOGGER_LEVEL=DEBUG

# APROC & AGATE
export ARLAS_URL_SEARCH="http://arlas-server:9999/arlas/explore/{collection}/_search?f=id:eq:{item}"
export AGATE_CORS_ORIGINS="*"
export AGATE_CORS_METHODS="*"
export AGATE_CORS_HEADERS="*"

# APROC
export APROC_CORS_ORIGINS="*"
export APROC_CORS_METHODS="*"
export APROC_CORS_HEADERS="*"
export ARLAS_SMTP_ACTIVATED=true
export ARLAS_SMTP_HOST=smtp4dev
export ARLAS_SMTP_PORT=25
export ARLAS_SMTP_USERNAME=whatever
export ARLAS_SMTP_PASSWORD=whatever
export ARLAS_SMTP_FROM=noreply@arlas.io
export APROC_DOWNLOAD_OUTBOX_DIR=/outbox
export APROC_DOWNLOAD_ADMIN_EMAILS="admin@the.boss,someone.else@the.boss"

export APROC_DOWNLOAD_SUBJECT_USER="\"ARLAS Services: Your download of {collection}/{item_id} is available.\""
export APROC_DOWNLOAD_CONTENT_USER="\"ARLAS Services: Dear {arlas-user-email}. <br>Your download of {collection}/{item_id} is available for projection {target_projection} ({target_format}). <br>ARLAS Services.\""

export APROC_DOWNLOAD_REQUEST_SUBJECT_USER="\"ARLAS Services: Thank you for your download request (({collection}/{item_id}).\""
export APROC_DOWNLOAD_REQUEST_CONTENT_USER="\"ARLAS Services: Dear {arlas-user-email}. <br>Your download request for {collection}/{item_id} with projection {target_projection} ({target_format}) will shortly be taken into account. <br>ARLAS Services.\""

export APROC_DOWNLOAD_SUBJECT_ERROR="\"ARLAS Services: ERROR: The download of {collection}/{item_id} failed.\""
export APROC_DOWNLOAD_CONTENT_ERROR="\"ARLAS Services: The download of {collection}/{item_id} failed ({error}).\""

export APROC_DOWNLOAD_SUBJECT_ADMIN="\"ARLAS Services: The download of {collection}/{item_id} for {arlas-user-email} is available.\""
export APROC_DOWNLOAD_CONTENT_ADMIN="\"ARLAS Services: The download of {collection}/{item_id} for {arlas-user-email} is available in {target_directory} ({file_name}) for projection {target_projection} ({target_format}). <br>ARLAS Services.\""

export APROC_DOWNLOAD_REQUEST_SUBJECT_ADMIN="\"ARLAS Services: {arlas-user-email} requested the download of {collection}/{item_id}.\""
export APROC_DOWNLOAD_REQUEST_CONTENT_ADMIN="\"ARLAS Services: {arlas-user-email} requested the download of {collection}/{item_id} for projection {target_projection} ({target_format}). <br>ARLAS Services.\""

export DOWNLOAD_S3_BUCKET=downloads
#export DOWNLOAD_S3_BUCKET=
export DOWNLOAD_S3_ACCESS_KEY_ID=airs
export DOWNLOAD_S3_SECRET_ACCESS_KEY=airssecret
export DOWNLOAD_S3_ENDPOINT_URL=http://minio:9000
export DOWNLOAD_S3_ASSET_HTTP_ENDPOINT_URL=http://minio:9000/{}/{}
export CLEAN_DOWNLOAD_OUTBOX_DIR=False

export APROC_EMAIL_PATH_PREFIX_ADD="Y://DISK1"
export APROC_PATH_TO_WINDOWS=true
export APROC_LOGGER_LEVEL=DEBUG
export APROC_ENDPOINT_FROM_APROC=http://aproc-service:8001/arlas/aproc
export APROC_INDEX_ENDPOINT_URL=http://elasticsearch:9200
export APROC_INDEX_NAME=aproc_downloads
export APROC_RESOURCE_ID_HASH_STARTS_AT=1

export APROC_INPUT_STORAGE_TYPE="gs"
# Google Storage
export APROC_INPUT_STORAGE_BUCKET="gisaia-public"
export APROC_INPUT_STORAGE_API_KEY_PROJECT=""
export APROC_INPUT_STORAGE_API_KEY_PRIVATE_KEY_ID=""
export APROC_INPUT_STORAGE_API_KEY_PRIVATE_KEY=""
# HTTPS
export APROC_INPUT_STORAGE_HEADERS="{}"
export APROC_INPUT_STORAGE_DOMAIN=""

# AGATE
export AGATE_PREFIX=/arlas/agate
export AGATE_HOST=0.0.0.0
export AGATE_PORT=8004
export AGATE_ENDPOINT=http://localhost:8004/arlas/agate/authorization
export AGATE_URL_HEADER=X-Forwarded-Uri
export AGATE_URL_HEADER_PREFIX=/object
export ASSET_MINIO_PATTERN="(/collections/)(?P<collection>[^/]+)/items/(?P<item>[^/]+)/assets/(?P<asset>[^/]+)"
export ASSET_MINIO_PUBLIC_PATTERN="(/collections/)(?P<collection>[^/]+)/items/(?P<item>[^/]+)/assets/thumbnail"
export AGATE_LOGGER_LEVEL=DEBUG

# FAM
export INGESTED_FOLDER=/inputs
export FAM_LOGGER_LEVEL=DEBUG
export FAM_CORS_ORIGINS="*"
export FAM_CORS_METHODS="*"
export FAM_CORS_HEADERS="*"
export PLATFORM='amd64'
