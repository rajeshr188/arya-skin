#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/staging}
compose_file=${2:-compose.staging.yml}
cd "$deployment_directory"

docker compose --file "$compose_file" exec -T web \
    python manage.py purge_closed_enquiries
