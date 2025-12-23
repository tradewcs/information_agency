#!/usr/bin/env bash

set -o errexit

export DJANGO_SETTINGS_MODULE=my_project.settings.prod

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
python manage.py loaddata data.json
