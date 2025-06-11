#!/bin/sh

fetchSettings(){
  echo "Download settings file from \"${ARLAS_IAM_SETTINGS_URL}\" ..."
  curl ${ARLAS_IAM_SETTINGS_URL} -o /usr/share/nginx/html/settings.yaml && echo "settings.yaml file downloaded with success." || (echo "Failed to download the settings.yaml file."; exit 1)
}

### URL to SETTINGS
if [ -z "${ARLAS_IAM_SETTINGS_URL}" ]; then
  echo "The default settings.yaml file is used"
else
  fetchSettings;
fi


# Set App base path
if [ -z "${FAM_WUI_APP_PATH}" ]; then
  FAM_WUI_APP_PATH=""
  export FAM_WUI_APP_PATH
  echo "No specific path for the app"
else
  echo ${FAM_WUI_APP_PATH}  "is used as app base path "
fi

envsubst '$FAM_WUI_APP_PATH' < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp
mv /etc/nginx/conf.d/default.conf.tmp /etc/nginx/conf.d/default.conf

# Set App base href
if [ -z "${FAM_WUI_BASE_HREF}" ]; then
  FAM_WUI_BASE_HREF=""
  export FAM_WUI_BASE_HREF
  echo "No specific base href for the app"
else
  echo ${FAM_WUI_BASE_HREF}  "is used as app base href "
fi

envsubst '$FAM_WUI_BASE_HREF' < /usr/share/nginx/html/index.html > /usr/share/nginx/html/index.html.tmp
mv /usr/share/nginx/html/index.html.tmp /usr/share/nginx/html/index.html

### Array of statics links
if [ -z "${ARLAS_STATIC_LINKS}" ]; then
  ARLAS_STATIC_LINKS="[]"
  export ARLAS_STATIC_LINKS
  echo "None static link is defined"
else
  echo ${ARLAS_STATIC_LINKS} "is used for 'links' in settings.yaml file"
fi
envsubst '$ARLAS_STATIC_LINKS' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml


## AUTHENTICATION
### ARLAS_USE_AUTHENT
if [ -z "${ARLAS_USE_AUTHENT}" ]; then
  ARLAS_USE_AUTHENT=false
  export ARLAS_USE_AUTHENT
  echo "No Authentication variable is set"
else
  echo ${ARLAS_USE_AUTHENT} "is used for 'authentication.use_authent'. Default value is 'false'"
fi
envsubst '$ARLAS_USE_AUTHENT' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_USE_AUTHENT
if [ -z "${ARLAS_AUTHENT_FORCE_CONNECT}" ]; then
  ARLAS_AUTHENT_FORCE_CONNECT=false
  export ARLAS_AUTHENT_FORCE_CONNECT
  echo "No Authentication force_connect variable is set"
else
  echo ${ARLAS_AUTHENT_FORCE_CONNECT} "is used for 'authentication.force_connect'. Default value is 'false'"
fi
envsubst '$ARLAS_AUTHENT_FORCE_CONNECT' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_USE_DISCOVERY
if [ -z "${ARLAS_AUTHENT_USE_DISCOVERY}" ]; then
  ARLAS_AUTHENT_USE_DISCOVERY=false
  export ARLAS_AUTHENT_USE_DISCOVERY
  echo "No Authentication discovery variable is set"
else
  echo ${ARLAS_AUTHENT_USE_DISCOVERY} "is used for 'authentication.use_discovery'. Default value is 'false'"
fi
envsubst '$ARLAS_AUTHENT_USE_DISCOVERY' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_ISSUER
if [ -z "${ARLAS_AUTHENT_ISSUER}" ]; then
  ARLAS_AUTHENT_ISSUER=NOT_CONFIGURED
  export ARLAS_AUTHENT_ISSUER
  echo "No Authentication issuer variable is set"
else
  echo ${ARLAS_AUTHENT_ISSUER} "is used for 'authentication.issuer'"
fi
envsubst '$ARLAS_AUTHENT_ISSUER' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_CLIENT_ID
if [ -z "${ARLAS_AUTHENT_CLIENT_ID}" ]; then
  ARLAS_AUTHENT_CLIENT_ID=NOT_CONFIGURED
  export ARLAS_AUTHENT_CLIENT_ID
  echo "No Authentication client_id variable is set"
else
  echo ${ARLAS_AUTHENT_CLIENT_ID} "is used for 'authentication.client_id'"
fi
envsubst '$ARLAS_AUTHENT_CLIENT_ID' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_REDIRECT_URI
if [ -z "${ARLAS_AUTHENT_REDIRECT_URI}" ]; then
  ARLAS_AUTHENT_REDIRECT_URI=NOT_CONFIGURED
  export ARLAS_AUTHENT_REDIRECT_URI
  echo "No Authentication redirect_uri variable is set"
else
  echo ${ARLAS_AUTHENT_REDIRECT_URI} "is used for 'authentication.redirect_uri'"
fi
envsubst '$ARLAS_AUTHENT_REDIRECT_URI' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI
if [ -z "${ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI}" ]; then
  ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI=NOT_CONFIGURED
  export ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI
  echo "No Authentication silent_refresh_redirect_uri variable is set"
else
  echo ${ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI} "is used for 'authentication.silent_refresh_redirect_uri'"
fi
envsubst '$ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_SCOPE
if [ -z "${ARLAS_AUTHENT_SCOPE}" ]; then
  ARLAS_AUTHENT_SCOPE="NOT_CONFIGURED"
  export ARLAS_AUTHENT_SCOPE
  echo "No Authentication scope variable is set"
else
  echo ${ARLAS_AUTHENT_SCOPE} "is used for 'authentication.scope'"
fi
envsubst '$ARLAS_AUTHENT_SCOPE' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_TOKEN_ENDPOINT
if [ -z "${ARLAS_AUTHENT_TOKEN_ENDPOINT}" ]; then
  ARLAS_AUTHENT_TOKEN_ENDPOINT="NOT_CONFIGURED"
  export ARLAS_AUTHENT_TOKEN_ENDPOINT
  echo "No Authentication token_endpoint variable is set"
else
  echo ${ARLAS_AUTHENT_TOKEN_ENDPOINT} "is used for 'authentication.token_endpoint'"
fi
envsubst '$ARLAS_AUTHENT_TOKEN_ENDPOINT' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_USERINFO_ENDPOINT
if [ -z "${ARLAS_AUTHENT_USERINFO_ENDPOINT}" ]; then
  ARLAS_AUTHENT_USERINFO_ENDPOINT="NOT_CONFIGURED"
  export ARLAS_AUTHENT_USERINFO_ENDPOINT
  echo "No Authentication userinfo_endpoint variable is set"
else
  echo ${ARLAS_AUTHENT_USERINFO_ENDPOINT} "is used for 'authentication.userinfo_endpoint'"
fi
envsubst '$ARLAS_AUTHENT_USERINFO_ENDPOINT' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_JWKS_ENDPOINT
if [ -z "${ARLAS_AUTHENT_JWKS_ENDPOINT}" ]; then
  ARLAS_AUTHENT_JWKS_ENDPOINT="NOT_CONFIGURED"
  export ARLAS_AUTHENT_JWKS_ENDPOINT
  echo "No Authentication jwks_endpoint variable is set"
else
  echo ${ARLAS_AUTHENT_JWKS_ENDPOINT} "is used for 'authentication.jwks_endpoint'"
fi
envsubst '$ARLAS_AUTHENT_JWKS_ENDPOINT' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_LOGIN_URL
if [ -z "${ARLAS_AUTHENT_LOGIN_URL}" ]; then
  ARLAS_AUTHENT_LOGIN_URL="NOT_CONFIGURED"
  export ARLAS_AUTHENT_LOGIN_URL
  echo "No Authentication login_url variable is set"
else
  echo ${ARLAS_AUTHENT_LOGIN_URL} "is used for 'authentication.login_url'"
fi
envsubst '$ARLAS_AUTHENT_LOGIN_URL' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_LOGOUT_URL
if [ -z "${ARLAS_AUTHENT_LOGOUT_URL}" ]; then
  ARLAS_AUTHENT_LOGOUT_URL="NOT_CONFIGURED"
  export ARLAS_AUTHENT_LOGOUT_URL
  echo "No Authentication logout_url variable is set"
else
  echo ${ARLAS_AUTHENT_LOGOUT_URL} "is used for 'authentication.logout_url'"
fi
envsubst '$ARLAS_AUTHENT_LOGOUT_URL' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_SHOW_DEBUG
if [ -z "${ARLAS_AUTHENT_SHOW_DEBUG}" ]; then
  ARLAS_AUTHENT_SHOW_DEBUG=false
  export ARLAS_AUTHENT_SHOW_DEBUG
  echo "No Authentication show_debug_information variable is set. Default value is 'false'"
else
  echo ${ARLAS_AUTHENT_SHOW_DEBUG} "is used for 'authentication.show_debug_information'"
fi
envsubst '$ARLAS_AUTHENT_SHOW_DEBUG' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_REQUIRE_HTTPS
if [ -z "${ARLAS_AUTHENT_REQUIRE_HTTPS}" ]; then
  ARLAS_AUTHENT_REQUIRE_HTTPS=true
  export ARLAS_AUTHENT_REQUIRE_HTTPS
  echo "No Authentication require_https variable is set. Default value is 'true'"
else
  echo ${ARLAS_AUTHENT_REQUIRE_HTTPS} "is used for 'authentication.require_https'"
fi
envsubst '$ARLAS_AUTHENT_REQUIRE_HTTPS' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_RESPONSE_TYPE
if [ -z "${ARLAS_AUTHENT_RESPONSE_TYPE}" ]; then
  ARLAS_AUTHENT_RESPONSE_TYPE="NOT_CONFIGURED"
  export ARLAS_AUTHENT_RESPONSE_TYPE
  echo "No Authentication response_type variable is set."
else
  echo ${ARLAS_AUTHENT_RESPONSE_TYPE} "is used for 'authentication.response_type'"
fi
envsubst '$ARLAS_AUTHENT_RESPONSE_TYPE' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT
if [ -z "${ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT}" ]; then
  ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT=5000
  export ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT
  echo "No Authentication silent_refresh_timeout variable is set. Default value is 5000."
else
  echo ${ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT} "is used for 'authentication.silent_refresh_timeout'"
fi
envsubst '$ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_TIMEOUT_FACTOR
if [ -z "${ARLAS_AUTHENT_TIMEOUT_FACTOR}" ]; then
  ARLAS_AUTHENT_TIMEOUT_FACTOR=0.75
  export ARLAS_AUTHENT_TIMEOUT_FACTOR
  echo "No Authentication timeout_factor variable is set. Default value is 0.75"
else
  echo ${ARLAS_AUTHENT_TIMEOUT_FACTOR} "is used for 'authentication.timeout_factor'"
fi
envsubst '$ARLAS_AUTHENT_TIMEOUT_FACTOR' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_ENABLE_SESSION_CHECKS
if [ -z "${ARLAS_AUTHENT_ENABLE_SESSION_CHECKS}" ]; then
  ARLAS_AUTHENT_ENABLE_SESSION_CHECKS=true
  export ARLAS_AUTHENT_ENABLE_SESSION_CHECKS
  echo "No Authentication session_checks_enabled variable is set. Default value is 'true'"
else
  echo ${ARLAS_AUTHENT_ENABLE_SESSION_CHECKS} "is used for 'authentication.session_checks_enabled'"
fi
envsubst '$ARLAS_AUTHENT_ENABLE_SESSION_CHECKS' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_CLEAR_HASH
if [ -z "${ARLAS_AUTHENT_CLEAR_HASH}" ]; then
  ARLAS_AUTHENT_CLEAR_HASH=false
  export ARLAS_AUTHENT_CLEAR_HASH
  echo "No Authentication clear_hash_after_login variable is set. Default value is 'false'"
else
  echo ${ARLAS_AUTHENT_CLEAR_HASH} "is used for 'authentication.clear_hash_after_login'"
fi
envsubst '$ARLAS_AUTHENT_CLEAR_HASH' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_STORAGE
if [ -z "${ARLAS_AUTHENT_STORAGE}" ]; then
  ARLAS_AUTHENT_STORAGE=localstorage
  export ARLAS_AUTHENT_STORAGE
  echo "No Authentication storage variable is set. Default value is 'localstorage'"
else
  echo ${ARLAS_AUTHENT_STORAGE} "is used for 'authentication.storage'"
fi
envsubst '$ARLAS_AUTHENT_STORAGE' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK
if [ -z "${ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK}" ]; then
  ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK=false
  export ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK
  echo "No Authentication disable_at_hash_check variable is set. Default value is 'false'"
else
  echo ${ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK} "is used for 'authentication.disable_at_hash_check'"
fi
envsubst '$ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_DUMMY_CLIENT_SECRET
if [ -z "${ARLAS_AUTHENT_DUMMY_CLIENT_SECRET}" ]; then
  ARLAS_AUTHENT_DUMMY_CLIENT_SECRET=NOT_CONFIGURED
  export ARLAS_AUTHENT_DUMMY_CLIENT_SECRET
  echo "No Authentication dummy_client_secret variable is set. Default value is NOT_CONFIGURED"
else
  echo ${ARLAS_AUTHENT_DUMMY_CLIENT_SECRET} "is used for 'authentication.dummy_client_secret'"
fi
envsubst '$ARLAS_AUTHENT_DUMMY_CLIENT_SECRET' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml


### ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS
if [ -z "${ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS}" ]; then
  ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS="[]"
  export ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS
  echo "None Authentication custom query params is defined"
else
  echo ${ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS} "is used for 'authentication.custom_query_params' in settings.yaml file"
fi
envsubst '$ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_MODE
if [ -z "${ARLAS_AUTHENT_MODE}" ]; then
  ARLAS_AUTHENT_MODE='iam'
  export ARLAS_AUTHENT_MODE
  echo "Default auth.mod: 'iam' "
else
  echo ${ARLAS_AUTHENT_MODE} "is used for 'authentication.auth_mode'. Default value is 'iam'"
fi
envsubst '$ARLAS_AUTHENT_MODE' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### THRESHOLD
if [ -z "${ARLAS_AUTHENT_THRESHOLD}" ]; then
  ARLAS_AUTHENT_THRESHOLD=60000
  export ARLAS_AUTHENT_THRESHOLD
  echo "Default threshold: 60000"
else
  echo ${ARLAS_AUTHENT_THRESHOLD} "is used for 'authentication.threshold'. Default value is '60000'"
fi
envsubst '$ARLAS_AUTHENT_THRESHOLD' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_AUTHENT_SIGN_UP_ENABLED
if [ -z "${ARLAS_AUTHENT_SIGN_UP_ENABLED}" ]; then
  ARLAS_AUTHENT_SIGN_UP_ENABLED=false
  export ARLAS_AUTHENT_SIGN_UP_ENABLED
  echo "No Authentication sign_up_enabled variable is set. Default value is 'false'"
else
  echo ${ARLAS_AUTHENT_SIGN_UP_ENABLED} "is used for 'authentication.sign_up_enabled'"
fi
envsubst '$ARLAS_AUTHENT_SIGN_UP_ENABLED' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### ARLAS_IAM_SERVER_URL
if [ -z "${ARLAS_IAM_SERVER_URL}" ]; then
  ARLAS_IAM_SERVER_URL="http://localhost:9997"
  export ARLAS_IAM_SERVER_URL
  echo "Default url : http://localhost:9997"
else
  echo ${ARLAS_IAM_SERVER_URL} "is used for 'authentication.url'."
fi
envsubst '$ARLAS_IAM_SERVER_URL' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

## FAM ##
### FAM_SERVER_URL
if [ -z "${FAM_SERVER_URL}" ]; then
  FAM_SERVER_URL="https://localhost:81/fam"
  export FAM_SERVER_URL
  echo "Default url : https://localhost:81/fam"
else
  echo ${FAM_SERVER_URL} "is used for 'file_manager.url'."
fi
envsubst '$FAM_SERVER_URL' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### FAM_DEFAULT_PATH
if [ -z "${FAM_DEFAULT_PATH}" ]; then
  FAM_DEFAULT_PATH=""
  export FAM_DEFAULT_PATH
  echo "Default path : ''"
else
  echo ${FAM_DEFAULT_PATH} "is used for 'file_manager.default_path'."
fi
envsubst '$FAM_DEFAULT_PATH' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### FAM_COLLECTION
if [ -z "${FAM_COLLECTION}" ]; then
  FAM_COLLECTION="digitalearth.africa"
  export FAM_COLLECTION
  echo "Default url : digitalearth.africa"
else
  echo ${FAM_COLLECTION} "is used for 'file_manager.collection'."
fi
envsubst '$FAM_COLLECTION' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### FAM_ARCHIVES_PAGES_SIZE
if [ -z "${FAM_ARCHIVES_PAGES_SIZE}" ]; then
  export FAM_ARCHIVES_PAGES_SIZE=20
  echo "Default archives pages size: 20"
else
  echo ${FAM_ARCHIVES_PAGES_SIZE} "is used for 'file_manager.archives_page_size'."
fi
envsubst '$FAM_ARCHIVES_PAGES_SIZE' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### FAM_FILES_PAGES_SIZE
if [ -z "${FAM_FILES_PAGES_SIZE}" ]; then
  export FAM_FILES_PAGES_SIZE=50
  echo "Default archives pages size: 50"
else
  echo ${FAM_FILES_PAGES_SIZE} "is used for 'file_manager.files_page_size'."
fi
envsubst '$FAM_FILES_PAGES_SIZE' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

## APROC ##
### APROC_SERVER_URL
if [ -z "${APROC_SERVER_URL}" ]; then
  APROC_SERVER_URL="https://localhost:81/aproc"
  export APROC_SERVER_URL
  echo "Default url : https://localhost:81/aproc"
else
  echo ${APROC_SERVER_URL} "is used for 'jobs.url'."
fi
envsubst '$APROC_SERVER_URL' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### APROC_CATALOG
if [ -z "${APROC_CATALOG}" ]; then
  APROC_CATALOG="catalog"
  export APROC_CATALOG
  echo "Default catalog : catalog"
else
  echo ${APROC_CATALOG} "is used for 'jobs.catalog'."
fi
envsubst '$APROC_CATALOG' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### APROC_COLLECTION
if [ -z "${APROC_COLLECTION}" ]; then
  APROC_COLLECTION="digitalearth.africa"
  export APROC_COLLECTION
  echo "Default url : digitalearth.africa"
else
  echo ${APROC_COLLECTION} "is used for 'job.collection'."
fi
envsubst '$APROC_COLLECTION' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

## AIRS ##
### AIRS_SERVER_URL
if [ -z "${AIRS_SERVER_URL}" ]; then
  AIRS_SERVER_URL="https://localhost:81/airs"
  export AIRS_SERVER_URL
  echo "Default url : https://localhost:81/airs"
else
  echo ${AIRS_SERVER_URL} "is used for 'status.url'."
fi
envsubst '$AIRS_SERVER_URL' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

### AIRS_COLLECTION
if [ -z "${AIRS_COLLECTION}" ]; then
  AIRS_COLLECTION="digitalearth.africa"
  export AIRS_COLLECTION
  echo "Default url : digitalearth.africa"
else
  echo ${AIRS_COLLECTION} "is used for 'status.collection'."
fi
envsubst '$AIRS_COLLECTION' < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
mv /usr/share/nginx/html/settings.yaml.tmp /usr/share/nginx/html/settings.yaml

nginx -g "daemon off;"
