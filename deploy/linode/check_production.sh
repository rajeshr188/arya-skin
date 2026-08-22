#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/production}
cd "$deployment_directory"

set -a
. ./.env
set +a

root_status=$(curl --silent --show-error --output /dev/null \
    --write-out '%{http_code}' "https://$PRODUCTION_HOST/")
cms_status=$(curl --silent --show-error --output /dev/null \
    --write-out '%{http_code}' "https://$PRODUCTION_HOST/cms/")
health_status=$(curl --silent --show-error --output /dev/null \
    --write-out '%{http_code}' "https://$PRODUCTION_HOST/healthz/")
www_status=$(curl --silent --show-error --location --max-redirs 3 \
    --output /dev/null --write-out '%{http_code}' "https://$WWW_HOST/")

printf 'production_root=%s\n' "$root_status"
printf 'wagtail_admin_redirect=%s\n' "$cms_status"
printf 'public_health=%s\n' "$health_status"
printf 'www_redirect_destination=%s\n' "$www_status"

test "$root_status" = "200"
test "$cms_status" = "302"
test "$health_status" = "200"
test "$www_status" = "200"
