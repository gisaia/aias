#!/bin/sh
set -o errexit -o pipefail

# Set the default value for an environment variable if not already set
set_default_env_variable() {
    VARIABLE_NAME=$1
    VARIABLE_VALUE=$2
    CURRENT_VALUE=$(eval "echo \$$VARIABLE_NAME")
    if [ -z "$CURRENT_VALUE" ]; then
        eval "$VARIABLE_NAME=\"$VARIABLE_VALUE\""
        export "$VARIABLE_NAME"
        echo "Set $VARIABLE_NAME to '$(eval "echo \$$VARIABLE_NAME")'."
    else
        echo "$VARIABLE_NAME provided and is set to '$CURRENT_VALUE'."
    fi
}

set_default_env_variable "FAM_WUI_APP_PATH" ""
set_default_env_variable "FAM_WUI_BASE_HREF" ""
set_default_env_variable "ARLAS_STATIC_LINKS" "[]"
set_default_env_variable "ARLAS_USE_AUTHENT" "false"
set_default_env_variable "ARLAS_AUTHENT_FORCE_CONNECT" "false"
set_default_env_variable "ARLAS_AUTHENT_USE_DISCOVERY" "false"
set_default_env_variable "ARLAS_AUTHENT_ISSUER" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_CLIENT_ID" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_REDIRECT_URI" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_SCOPE" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_TOKEN_ENDPOINT" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_USERINFO_ENDPOINT" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_JWKS_ENDPOINT" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_LOGIN_URL" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_LOGOUT_URL" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_SHOW_DEBUG" "false"
set_default_env_variable "ARLAS_AUTHENT_REQUIRE_HTTPS" "true"
set_default_env_variable "ARLAS_AUTHENT_RESPONSE_TYPE" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT" "5000"
set_default_env_variable "ARLAS_AUTHENT_TIMEOUT_FACTOR" "0.75"
set_default_env_variable "ARLAS_AUTHENT_ENABLE_SESSION_CHECKS" "true"
set_default_env_variable "ARLAS_AUTHENT_CLEAR_HASH" "false"
set_default_env_variable "ARLAS_AUTHENT_STORAGE" "localstorage"
set_default_env_variable "ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK" "false"
set_default_env_variable "ARLAS_AUTHENT_DUMMY_CLIENT_SECRET" "NOT_CONFIGURED"
set_default_env_variable "ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS" "[]"
set_default_env_variable "ARLAS_AUTHENT_MODE" "iam"
set_default_env_variable "ARLAS_AUTHENT_THRESHOLD" "60000"
set_default_env_variable "ARLAS_AUTHENT_SIGN_UP_ENABLED" "false"
set_default_env_variable "ARLAS_IAM_SERVER_URL" "http://localhost:9997"
set_default_env_variable "FAM_SERVER_URL" "https://localhost:81/fam"
set_default_env_variable "FAM_DEFAULT_PATH" ""
set_default_env_variable "FAM_COLLECTION" "digitalearth.africa"
set_default_env_variable "FAM_ARCHIVES_PAGES_SIZE" "20"
set_default_env_variable "FAM_FILES_PAGES_SIZE" "50"
set_default_env_variable "APROC_SERVER_URL" "https://localhost:81/aproc"
set_default_env_variable "APROC_CATALOG" "catalog"
set_default_env_variable "APROC_COLLECTION" "digitalearth.africa"
set_default_env_variable "AIRS_SERVER_URL" "https://localhost:81/airs"
set_default_env_variable "AIRS_COLLECTION" "digitalearth.africa"





SETTINGS_VARS="FAM_WUI_APP_PATH
    FAM_WUI_BASE_HREF
    ARLAS_STATIC_LINKS
    ARLAS_USE_AUTHENT
    ARLAS_AUTHENT_FORCE_CONNECT
    ARLAS_AUTHENT_USE_DISCOVERY
    ARLAS_AUTHENT_ISSUER
    ARLAS_AUTHENT_CLIENT_ID
    ARLAS_AUTHENT_REDIRECT_URI
    ARLAS_AUTHENT_SILENT_REFRESH_REDIRECT_URI
    ARLAS_AUTHENT_SCOPE
    ARLAS_AUTHENT_TOKEN_ENDPOINT
    ARLAS_AUTHENT_USERINFO_ENDPOINT
    ARLAS_AUTHENT_JWKS_ENDPOINT
    ARLAS_AUTHENT_LOGIN_URL
    ARLAS_AUTHENT_LOGOUT_URL
    ARLAS_AUTHENT_SHOW_DEBUG
    ARLAS_AUTHENT_REQUIRE_HTTPS
    ARLAS_AUTHENT_RESPONSE_TYPE
    ARLAS_AUTHENT_SILENT_REFRESH_TIMEOUT
    ARLAS_AUTHENT_TIMEOUT_FACTOR
    ARLAS_AUTHENT_ENABLE_SESSION_CHECKS
    ARLAS_AUTHENT_CLEAR_HASH
    ARLAS_AUTHENT_STORAGE
    ARLAS_AUTHENT_DISABLE_AT_HASH_CHECK
    ARLAS_AUTHENT_DUMMY_CLIENT_SECRET
    ARLAS_AUTHENT_CUSTOM_QUERY_PARAMS
    ARLAS_AUTHENT_MODE
    ARLAS_AUTHENT_THRESHOLD
    ARLAS_AUTHENT_SIGN_UP_ENABLED
    ARLAS_IAM_SERVER_URL
    FAM_SERVER_URL
    FAM_DEFAULT_PATH
    FAM_COLLECTION
    FAM_ARCHIVES_PAGES_SIZE
    FAM_FILES_PAGES_SIZE
    APROC_SERVER_URL
    APROC_CATALOG
    APROC_COLLECTION
    AIRS_SERVER_URL
    AIRS_COLLECTION"

SETTINGS_SUBST=$(printf '$%s ' $SETTINGS_VARS)
envsubst "$SETTINGS_SUBST" < /usr/share/nginx/html/settings.yaml > /usr/share/nginx/html/settings.yaml.tmp
truncate -s 0 /usr/share/nginx/html/settings.yaml
cat /usr/share/nginx/html/settings.yaml.tmp >> /usr/share/nginx/html/settings.yaml

# Variables to substitute in index.html
INDEX_VARS="FAM_WUI_BASE_HREF"

INDEX_SUBST=$(printf '$%s ' $INDEX_VARS)
envsubst "$INDEX_SUBST" < /usr/share/nginx/html/index.html > /usr/share/nginx/html/index.html.tmp
cat /usr/share/nginx/html/index.html.tmp > /usr/share/nginx/html/index.html

# Variables to substitute in nginx default.conf
NGINX_VARS="FAM_WUI_APP_PATH"

NGINX_SUBST=$(printf '$%s ' $NGINX_VARS)
envsubst "$NGINX_SUBST" < /etc/nginx/conf.d/default.conf > /etc/nginx/conf.d/default.conf.tmp
cat /etc/nginx/conf.d/default.conf.tmp > /etc/nginx/conf.d/default.conf

nginx -g "daemon off;"
