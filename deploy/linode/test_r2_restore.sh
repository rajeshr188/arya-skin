#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/staging}
backup_directory=${2:-/srv/arya-skin/backups}
compose_file=${3:-compose.staging.yml}
private_key=${4:-/srv/arya-skin/secrets/backup-recovery-key.agekey}

cd "$deployment_directory"
set -a
. ./.env
set +a

r2_backup_environment=${R2_BACKUP_ENV_FILE:-/srv/arya-skin/secrets/r2-backups.env}
test -r "$r2_backup_environment"
test -r "$private_key"
test -n "${APP_IMAGE:-}"
backup_image=${BACKUP_APP_IMAGE:-$APP_IMAGE}

backup_directory=$(cd "$backup_directory" && pwd -P)
restore_directory=$(mktemp -d "$backup_directory/.r2-restore-test.XXXXXX")
encrypted_backup="$restore_directory/latest.backup.tar.age"
bundle="$restore_directory/latest.backup.tar"
files_directory="$restore_directory/files"
restore_database="arya_r2_restore_$(date -u +%Y%m%d%H%M%S)_$$"

cleanup() {
    docker compose --file "$compose_file" exec -T db \
        dropdb --username "$POSTGRES_USER" --if-exists --force \
        "$restore_database" > /dev/null 2>&1 || true
    case "$restore_directory" in
        "$backup_directory"/.r2-restore-test.*)
            rm -rf -- "$restore_directory"
            ;;
    esac
}
trap cleanup EXIT HUP INT TERM

docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env-file "$r2_backup_environment" \
    --volume "$restore_directory:/restore" \
    "$backup_image" \
    python scripts/r2_backup.py download-latest \
    --output /restore/latest.backup.tar.age

age --decrypt --identity "$private_key" --output "$bundle" "$encrypted_backup"
mkdir "$files_directory"
tar --extract --file "$bundle" --directory "$files_directory"

database_backup=$(find "$files_directory" -maxdepth 1 -type f \
    -name 'arya-skin-*.database.dump' | sort | tail -n 1)
test -n "$database_backup"
prefix=${database_backup%.database.dump}
manifest="$prefix.sha256"
test -f "$manifest"
(
    cd "$files_directory"
    sha256sum --check "$(basename "$manifest")"
)

docker compose --file "$compose_file" exec -T db \
    createdb --username "$POSTGRES_USER" "$restore_database"
docker compose --file "$compose_file" exec -T db \
    pg_restore --username "$POSTGRES_USER" --dbname "$restore_database" \
    --exit-on-error --no-owner --no-privileges < "$database_backup"
docker compose --file "$compose_file" exec -T db \
    psql --username "$POSTGRES_USER" --dbname "$restore_database" \
    --tuples-only --no-align \
    --command 'SELECT count(*) FROM django_migrations;' > /dev/null

media_backup="$prefix.media.tar.gz"
if [ -f "$media_backup" ]; then
    gzip --test "$media_backup"
fi

cleanup
trap - EXIT HUP INT TERM
printf 'r2_restore_test=passed\n'
printf 'restored_backup=%s\n' "$(basename "$prefix")"
