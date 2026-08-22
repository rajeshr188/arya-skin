#!/bin/sh
set -eu

deployment_directory=${1:-/srv/arya-skin/staging}
cd "$deployment_directory"

docker compose --file compose.staging.yml exec -T web \
    python manage.py purge_closed_enquiries
