#!/bin/sh
set -eu

destination=${1:-/srv/arya-skin/staging/.env}
app_image=${2:-arya-skin:staging}
staging_host=${3:-staging.drnareshrathod.com}

if [ -e "$destination" ]; then
    echo "Refusing to overwrite existing environment: $destination" >&2
    exit 1
fi

directory=$(dirname "$destination")
install -d -m 750 "$directory"
temporary_file=$(mktemp)
trap 'rm -f "$temporary_file"' EXIT
umask 077

secret_key=$(openssl rand -hex 48)
postgres_password=$(openssl rand -hex 32)
staging_password=$(openssl rand -hex 24)

{
    printf 'APP_IMAGE=%s\n' "$app_image"
    printf 'STAGING_HOST=%s\n' "$staging_host"
    printf 'DJANGO_ENVIRONMENT=staging\n'
    printf 'DJANGO_DEBUG=False\n'
    printf 'SECRET_KEY=%s\n' "$secret_key"
    printf 'POSTGRES_DB=arya_skin\n'
    printf 'POSTGRES_USER=arya_skin\n'
    printf 'POSTGRES_PASSWORD=%s\n' "$postgres_password"
    printf 'ALLOWED_HOSTS=%s\n' "$staging_host"
    printf 'CSRF_TRUSTED_ORIGINS=https://%s\n' "$staging_host"
    printf 'WAGTAILADMIN_BASE_URL=https://%s\n' "$staging_host"
    printf 'STAGING_ACCESS_USERNAME=reviewer\n'
    printf 'STAGING_ACCESS_PASSWORD=%s\n' "$staging_password"
    printf 'TRUST_X_FORWARDED_PROTO=True\n'
    printf 'HEALTH_CHECK_HOST=%s\n' "$staging_host"
    printf 'WEB_CONCURRENCY=1\n'
    printf 'GUNICORN_THREADS=2\n'
    printf 'LOG_LEVEL=INFO\n'
} > "$temporary_file"

install -m 600 "$temporary_file" "$destination"
echo "Created $destination with mode 600."
echo "Retrieve reviewer credentials locally over SSH; do not copy .env into Git."
