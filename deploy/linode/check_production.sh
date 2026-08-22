#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/production}
cd "$deployment_directory"

set -a
. ./.env
set +a

test -r "$R2_MEDIA_ENV_FILE"
set -a
. "$R2_MEDIA_ENV_FILE"
set +a

expect_status() {
    label=$1
    url=$2
    expected=$3
    status=$(curl --silent --show-error --output /dev/null \
        --write-out '%{http_code}' "$url")
    printf '%s=%s\n' "$label" "$status"
    test "$status" = "$expected"
}

expect_status production_root "https://$PRODUCTION_HOST/" 200
expect_status doctor_page "https://$PRODUCTION_HOST/profile/" 200
expect_status clinics_index "https://$PRODUCTION_HOST/clinics/" 200
expect_status sitapura_clinic "https://$PRODUCTION_HOST/clinics/sitapura/" 200
expect_status chaksu_clinic "https://$PRODUCTION_HOST/clinics/chaksu/" 200
expect_status contact_page "https://$PRODUCTION_HOST/contact/" 200
expect_status privacy_page "https://$PRODUCTION_HOST/privacy/" 200
expect_status disclaimer_page "https://$PRODUCTION_HOST/medical-disclaimer/" 200
expect_status appointment_form "https://$PRODUCTION_HOST/appointments/request/" 200
expect_status robots_txt "https://$PRODUCTION_HOST/robots.txt" 200
expect_status sitemap_xml "https://$PRODUCTION_HOST/sitemap.xml" 200
expect_status treatments_unpublished "https://$PRODUCTION_HOST/treatments/" 404
expect_status articles_unpublished "https://$PRODUCTION_HOST/blog/" 404
expect_status wagtail_admin_redirect "https://$PRODUCTION_HOST/cms/" 302
expect_status public_health "https://$PRODUCTION_HOST/healthz/" 200
expect_status portrait_media \
    "https://$R2_MEDIA_CUSTOM_DOMAIN/original_images/nareshbust.png" 200

www_status=$(curl --silent --show-error --location --max-redirs 3 \
    --output /dev/null --write-out '%{http_code}' "https://$WWW_HOST/")
printf 'www_redirect_destination=%s\n' "$www_status"
test "$www_status" = "200"

response_headers=$(mktemp)
response_body=$(mktemp)
robots_body=$(mktemp)
cleanup() {
    rm -f -- "$response_headers" "$response_body" "$robots_body"
}
trap cleanup EXIT HUP INT TERM

curl --silent --show-error --dump-header "$response_headers" \
    --output "$response_body" "https://$PRODUCTION_HOST/"
curl --silent --show-error --output "$robots_body" \
    "https://$PRODUCTION_HOST/robots.txt"

grep --fixed-strings --quiet \
    "<link rel=\"canonical\" href=\"https://$PRODUCTION_HOST/\">" \
    "$response_body"
grep --fixed-strings --quiet \
    "Sitemap: https://$PRODUCTION_HOST/sitemap.xml" "$robots_body"
if grep --ignore-case --quiet '^x-robots-tag:.*noindex' "$response_headers"; then
    echo "Production homepage unexpectedly has a noindex header." >&2
    exit 1
fi
if grep --extended-regexp --quiet 'href="/(treatments|blog)/"' "$response_body"; then
    echo "An unpublished empty index still appears in navigation." >&2
    exit 1
fi

grep --ignore-case --quiet '^strict-transport-security: max-age=300' \
    "$response_headers"
grep --ignore-case --quiet '^x-content-type-options: nosniff' \
    "$response_headers"
grep --ignore-case --quiet '^x-frame-options: deny' "$response_headers"
grep --ignore-case --quiet \
    '^referrer-policy: strict-origin-when-cross-origin' "$response_headers"

printf 'canonical_origin=verified\n'
printf 'robots_sitemap=verified\n'
printf 'production_noindex=absent\n'
printf 'empty_index_navigation_links=absent\n'
printf 'initial_security_headers=verified\n'
