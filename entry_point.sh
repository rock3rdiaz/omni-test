#!/bin/bash
export DJANGO_SETTINGS=$DJANGO_SETTINGS_MODULE
export DEFAULT_BIND=0.0.0.0:$PUBLISHED_PORT
export DEFAULT_WORKERS=6
python omni/manage.py makemigrations --no-input
python omni/manage.py migrate
python omni/manage.py collectstatic --no-input
python omni/manage.py initadmin
service nginx start
gunicorn omni.wsgi --env DJANGO_SETTINGS_MODULE="${DJANGO_SETTINGS}" --bind "${DEFAULT_BIND}" --workers=${DEFAULT_WORKERS} --log-level debug --chdir ./omni