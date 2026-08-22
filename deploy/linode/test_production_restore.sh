#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/production}
backup_directory=${2:-/srv/arya-skin/backups}

cd "$deployment_directory"
set -a
. ./.env
set +a

backup_directory=$(cd "$backup_directory" && pwd -P)
database_backup=$(find "$backup_directory" -maxdepth 1 -type f \
    -name 'arya-skin-production-*.database.dump' | sort | tail -n 1)
test -n "$database_backup"

prefix=${database_backup%.database.dump}
manifest="$prefix.sha256"
test -f "$manifest"

(
    cd "$backup_directory"
    sha256sum --check "$(basename "$manifest")"
)

restore_database="arya_production_restore_$(date -u +%Y%m%d%H%M%S)_$$"
cleanup() {
    docker compose --file compose.production.yml exec -T db \
        dropdb --username "$POSTGRES_USER" --if-exists --force \
        "$restore_database" > /dev/null 2>&1 || true
}
trap cleanup EXIT HUP INT TERM

docker compose --file compose.production.yml exec -T db \
    createdb --username "$POSTGRES_USER" "$restore_database"
docker compose --file compose.production.yml exec -T db \
    pg_restore --username "$POSTGRES_USER" --dbname "$restore_database" \
    --exit-on-error --no-owner --no-privileges < "$database_backup"
docker compose --file compose.production.yml exec -T db \
    psql --username "$POSTGRES_USER" --dbname "$restore_database" \
    --tuples-only --no-align \
    --command 'SELECT count(*) FROM django_migrations;' > /dev/null

cleanup
trap - EXIT HUP INT TERM
printf 'production_restore_test=passed\n'
printf 'backup=%s\n' "$(basename "$prefix")"
