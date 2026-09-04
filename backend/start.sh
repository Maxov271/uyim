#!/bin/sh
set -e

# Har deployda avtomatik: migratsiya + statik fayllar allaqachon build vaqtida yig'ilgan.
python manage.py migrate --noinput

# Demo katalog: tabiiy kalitlar bo'yicha upsert qiladi, shuning uchun har deployda
# qayta ishga tushirish xavfsiz (backend/README.md: "Seed data" bo'limi).
# Coolify Terminal ishlamagan holatlarda ham katalog bo'sh qolmasligi uchun avtomatik.
python manage.py seed_demo || true

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
