#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/production}
backup_directory=${2:-/srv/arya-skin/backups}
retention_days=${BACKUP_RETENTION_DAYS:-14}

case "$retention_days" in
    ''|*[!0-9]*)
        printf 'BACKUP_RETENTION_DAYS must be a non-negative integer\n' >&2
        exit 2
        ;;
esac

cd "$deployment_directory"
set -a
. ./.env
set +a

umask 077
mkdir -p "$backup_directory"
backup_directory=$(cd "$backup_directory" && pwd -P)
timestamp=$(date -u +%Y%m%dT%H%M%SZ)
prefix="arya-skin-production-$timestamp"
database_backup="$backup_directory/$prefix.database.dump"
manifest="$backup_directory/$prefix.sha256"
database_temporary="$database_backup.temporary"
manifest_temporary="$manifest.temporary"

cleanup() {
    rm -f -- "$database_temporary" "$manifest_temporary"
}
trap cleanup EXIT HUP INT TERM

docker compose --file compose.production.yml exec -T db \
    pg_dump --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" \
    --format=custom --no-owner --no-privileges > "$database_temporary"
test -s "$database_temporary"
docker compose --file compose.production.yml exec -T db \
    pg_restore --list < "$database_temporary" > /dev/null

mv "$database_temporary" "$database_backup"
(
    cd "$backup_directory"
    sha256sum "$(basename "$database_backup")"
) > "$manifest_temporary"
mv "$manifest_temporary" "$manifest"

"$deployment_directory/encrypt_upload_latest_backup.sh" \
    "$deployment_directory" "$backup_directory" arya-skin-production

find "$backup_directory" -maxdepth 1 -type f \
    \( -name 'arya-skin-production-*.database.dump' \
    -o -name 'arya-skin-production-*.sha256' \) \
    -mtime "+$retention_days" -delete

trap - EXIT HUP INT TERM
printf 'backup=%s\n' "$prefix"
printf 'local_and_offsite_retention_days=%s\n' "$retention_days"
