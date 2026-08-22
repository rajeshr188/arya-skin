#!/bin/sh
set -eu

mode=${1:---dry-run}
deployment_directory=${2:-/srv/arya-skin/production}
cd "$deployment_directory"

set -a
. ./.env
set +a

case "$mode" in
    --dry-run)
        migration_argument=--dry-run
        ;;
    --execute)
        migration_argument=
        ;;
    *)
        echo "Usage: $0 [--dry-run|--execute] [deployment-directory]" >&2
        exit 2
        ;;
esac

test -r "$R2_MEDIA_ENV_FILE"
docker volume inspect "$MEDIA_IMPORT_VOLUME" >/dev/null

if [ -n "$migration_argument" ]; then
    docker run --rm \
        --env-file .env \
        --env-file "$R2_MEDIA_ENV_FILE" \
        --volume "$MEDIA_IMPORT_VOLUME:/app/media-import:ro" \
        "$APP_IMAGE" \
        python manage.py migrate_media_to_storage \
        --source /app/media-import "$migration_argument"
else
    docker run --rm \
        --env-file .env \
        --env-file "$R2_MEDIA_ENV_FILE" \
        --volume "$MEDIA_IMPORT_VOLUME:/app/media-import:ro" \
        "$APP_IMAGE" \
        python manage.py migrate_media_to_storage \
        --source /app/media-import
fi
