#!/bin/sh
set -e

# Har deployda avtomatik: migratsiya + statik fayllar allaqachon build vaqtida yig'ilgan.
python manage.py migrate --noinput

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
