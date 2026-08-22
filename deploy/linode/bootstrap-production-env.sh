#!/bin/sh
set -eu

staging_environment=${1:-/srv/arya-skin/staging/.env}
destination=${2:-/srv/arya-skin/production/.env}
app_image=${3:?Pass the immutable production image tag as argument 3}

if [ ! -r "$staging_environment" ]; then
    echo "Cannot read staging environment: $staging_environment" >&2
    exit 1
fi
if [ -e "$destination" ]; then
    echo "Refusing to overwrite existing environment: $destination" >&2
    exit 1
fi

set -a
. "$staging_environment"
set +a
: "${SECRET_KEY:?Staging SECRET_KEY is missing}"
: "${POSTGRES_DB:?Staging POSTGRES_DB is missing}"
: "${POSTGRES_USER:?Staging POSTGRES_USER is missing}"
: "${POSTGRES_PASSWORD:?Staging POSTGRES_PASSWORD is missing}"

directory=$(dirname "$destination")
install -d -m 750 "$directory"
temporary_file=$(mktemp)
trap 'rm -f "$temporary_file"' EXIT
umask 077

{
    printf 'APP_IMAGE=%s\n' "$app_image"
    printf 'PRODUCTION_HOST=drnareshrathod.com\n'
    printf 'WWW_HOST=www.drnareshrathod.com\n'
    printf 'DJANGO_ENVIRONMENT=production\n'
    printf 'DJANGO_DEBUG=False\n'
    printf 'SECRET_KEY=%s\n' "$SECRET_KEY"
    printf 'POSTGRES_DB=%s\n' "$POSTGRES_DB"
    printf 'POSTGRES_USER=%s\n' "$POSTGRES_USER"
    printf 'POSTGRES_PASSWORD=%s\n' "$POSTGRES_PASSWORD"
    printf 'DATABASE_URL=postgresql://%s:%s@db:5432/%s\n' \
        "$POSTGRES_USER" "$POSTGRES_PASSWORD" "$POSTGRES_DB"
    printf 'ALLOWED_HOSTS=drnareshrathod.com,www.drnareshrathod.com\n'
    printf 'CSRF_TRUSTED_ORIGINS=https://drnareshrathod.com,https://www.drnareshrathod.com\n'
    printf 'WAGTAILADMIN_BASE_URL=https://drnareshrathod.com\n'
    printf 'TRUST_X_FORWARDED_PROTO=True\n'
    printf 'HEALTH_CHECK_HOST=drnareshrathod.com\n'
    printf 'SITE_NOINDEX=False\n'
    printf 'SECURE_HSTS_SECONDS=300\n'
    printf 'SECURE_HSTS_INCLUDE_SUBDOMAINS=False\n'
    printf 'SECURE_HSTS_PRELOAD=False\n'
    printf 'WEB_CONCURRENCY=1\n'
    printf 'GUNICORN_THREADS=2\n'
    printf 'LOG_LEVEL=INFO\n'
    printf 'R2_MEDIA_ENV_FILE=/srv/arya-skin/secrets/r2-media.env\n'
    printf 'R2_BACKUP_ENV_FILE=/srv/arya-skin/secrets/r2-backups.env\n'
    printf 'BACKUP_AGE_RECIPIENT_FILE=/srv/arya-skin/secrets/backup-age-recipient.txt\n'
    printf 'POSTGRES_VOLUME=arya-skin-staging_postgres_data\n'
    printf 'MEDIA_IMPORT_VOLUME=arya-skin-staging_media_data\n'
    printf 'CADDY_DATA_VOLUME=arya-skin-staging_caddy_data\n'
    printf 'CADDY_CONFIG_VOLUME=arya-skin-staging_caddy_config\n'
} > "$temporary_file"

install -m 600 "$temporary_file" "$destination"
echo "Created $destination with mode 600 using the existing application and database secrets."
