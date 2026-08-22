#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/staging}
backup_directory=${2:-/srv/arya-skin/backups}
backup_prefix=${3:-arya-skin-staging}

cd "$deployment_directory"
set -a
. ./.env
set +a

r2_backup_environment=${R2_BACKUP_ENV_FILE:-/srv/arya-skin/secrets/r2-backups.env}
age_recipient_file=${BACKUP_AGE_RECIPIENT_FILE:-/srv/arya-skin/secrets/backup-age-recipient.txt}
test -r "$r2_backup_environment"
test -r "$age_recipient_file"
test -n "${APP_IMAGE:-}"
backup_image=${BACKUP_APP_IMAGE:-$APP_IMAGE}

backup_directory=$(cd "$backup_directory" && pwd -P)
database_backup=$(find "$backup_directory" -maxdepth 1 -type f \
    -name "$backup_prefix-*.database.dump" | sort | tail -n 1)
test -n "$database_backup"

prefix=${database_backup%.database.dump}
manifest="$prefix.sha256"
test -f "$manifest"
media_backup="$prefix.media.tar.gz"

set -- "$(basename "$database_backup")" "$(basename "$manifest")"
if [ -f "$media_backup" ]; then
    set -- "$@" "$(basename "$media_backup")"
fi

(
    cd "$backup_directory"
    sha256sum --check "$(basename "$manifest")"
)

encrypted_backup="$prefix.backup.tar.age"
encrypted_temporary="$encrypted_backup.temporary"
cleanup() {
    rm -f -- "$encrypted_temporary"
}
trap cleanup EXIT HUP INT TERM

recipient=$(tr -d '\r\n' < "$age_recipient_file")
case "$recipient" in
    age1*) ;;
    *)
        echo "Invalid age recipient file." >&2
        exit 2
        ;;
esac

(
    cd "$backup_directory"
    tar --create --file - "$@"
) | age --encrypt --recipient "$recipient" --output "$encrypted_temporary"
test -s "$encrypted_temporary"
mv "$encrypted_temporary" "$encrypted_backup"

container_backup="/backups/$(basename "$encrypted_backup")"
docker run --rm \
    --user "$(id -u):$(id -g)" \
    --env-file "$r2_backup_environment" \
    --volume "$backup_directory:/backups:ro" \
    "$backup_image" \
    python scripts/r2_backup.py upload --file "$container_backup"

rm -f -- "$encrypted_backup"
trap - EXIT HUP INT TERM
printf 'encrypted_backup_uploaded=%s\n' "$(basename "$encrypted_backup")"
