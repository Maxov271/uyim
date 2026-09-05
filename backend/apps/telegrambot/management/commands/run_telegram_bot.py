import asyncio

from django.core.management.base import BaseCommand

from apps.telegrambot.aiogram_bot import run_polling


class Command(BaseCommand):
    help = (
        "Runs the Uyim.uz Telegram bot with long polling (aiogram) — a continuously running "
        "process, no webhook/public URL needed. Intended to be kept alive indefinitely "
        "(see backend/start.sh's restart loop), not run once and exited."
    )

    def handle(self, *args, **options):
        asyncio.run(run_polling())
