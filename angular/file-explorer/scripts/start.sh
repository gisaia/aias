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
