#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/staging}
backup_directory=${2:-/srv/arya-skin/backups}

cd "$deployment_directory"
set -a
. ./.env
set +a

backup_directory=$(cd "$backup_directory" && pwd -P)
database_backup=$(find "$backup_directory" -maxdepth 1 -type f \
    -name 'arya-skin-staging-*.database.dump' | sort | tail -n 1)
test -n "$database_backup"

prefix=${database_backup%.database.dump}
media_backup="$prefix.media.tar.gz"
manifest="$prefix.sha256"
test -f "$media_backup"
test -f "$manifest"

(
    cd "$backup_directory"
    sha256sum --check "$(basename "$manifest")"
)

restore_database="arya_restore_$(date -u +%Y%m%d%H%M%S)_$$"
restore_directory=$(mktemp -d "$backup_directory/.restore-test.XXXXXX")

cleanup() {
    docker compose --file compose.staging.yml exec -T db \
        dropdb --username "$POSTGRES_USER" --if-exists --force \
        "$restore_database" > /dev/null 2>&1 || true
    case "$restore_directory" in
        "$backup_directory"/.restore-test.*)
            rm -rf -- "$restore_directory"
            ;;
    esac
}
trap cleanup EXIT HUP INT TERM

docker compose --file compose.staging.yml exec -T db \
    createdb --username "$POSTGRES_USER" "$restore_database"
docker compose --file compose.staging.yml exec -T db \
    pg_restore --username "$POSTGRES_USER" --dbname "$restore_database" \
    --exit-on-error --no-owner --no-privileges < "$database_backup"
docker compose --file compose.staging.yml exec -T db \
    psql --username "$POSTGRES_USER" --dbname "$restore_database" \
    --tuples-only --no-align \
    --command 'SELECT count(*) FROM django_migrations;' > /dev/null

tar --extract --gzip --file "$media_backup" --directory "$restore_directory"
test -d "$restore_directory"

cleanup
trap - EXIT HUP INT TERM
printf 'restore_test=passed\n'
printf 'backup=%s\n' "$(basename "$prefix")"
