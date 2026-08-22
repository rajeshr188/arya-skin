#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/staging}
cd "$deployment_directory"

set -a
. ./.env
set +a

root_status=$(curl --silent --show-error --user \
    "$STAGING_ACCESS_USERNAME:$STAGING_ACCESS_PASSWORD" \
    --output /dev/null --write-out '%{http_code}' \
    "https://$STAGING_HOST/")
cms_status=$(curl --silent --show-error --user \
    "$STAGING_ACCESS_USERNAME:$STAGING_ACCESS_PASSWORD" \
    --output /dev/null --write-out '%{http_code}' \
    "https://$STAGING_HOST/cms/")
health_status=$(curl --silent --show-error --output /dev/null \
    --write-out '%{http_code}' "https://$STAGING_HOST/healthz/")

printf 'authenticated_root=%s\n' "$root_status"
printf 'wagtail_admin_redirect=%s\n' "$cms_status"
printf 'public_health=%s\n' "$health_status"

test "$root_status" = "200"
test "$cms_status" = "302"
test "$health_status" = "200"
