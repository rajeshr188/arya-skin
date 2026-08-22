#!/bin/sh
set -eu

python manage.py check --deploy
python manage.py migrate --noinput
python manage.py collectstatic --noinput --verbosity 0
