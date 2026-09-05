#!/bin/sh
set -e

# Har deployda avtomatik: migratsiya + statik fayllar allaqachon build vaqtida yig'ilgan.
python manage.py migrate --noinput

# Demo katalog: tabiiy kalitlar bo'yicha upsert qiladi, shuning uchun har deployda
# qayta ishga tushirish xavfsiz (backend/README.md: "Seed data" bo'limi).
# Coolify Terminal ishlamagan holatlarda ham katalog bo'sh qolmasligi uchun avtomatik.
python manage.py seed_demo || true

# Telegram bot: webhook emas, doimiy ishlaydigan long-polling jarayoni (aiogram) —
# shu konteyner ichida fonda, gunicorn bilan bir vaqtda. TELEGRAM_BOT_TOKEN bo'sh bo'lsa
# run_telegram_bot darhol chiqadi (logga ogohlantirish yozib) — pastdagi tsikl uni
# qayta-qayta qayta ishga tushiraveradi, shuning uchun token keyinroq qo'shilsa ham
# konteyner qayta deploy qilinmasdan bot o'zi ishga tushadi.
(
  while true; do
    python manage.py run_telegram_bot
    echo "[telegram-bot] to'xtadi, 15 soniyadan keyin qayta urinamiz..."
    sleep 15
  done
) &

exec gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3
