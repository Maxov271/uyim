from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.telegrambot.client import TelegramClient


class Command(BaseCommand):
    help = "Registers the Telegram bot webhook at https://<public-host>/api/telegram/webhook/<secret>"

    def add_arguments(self, parser):
        parser.add_argument("public_base_url", help="e.g. https://api.uyim.uz")

    def handle(self, *args, **options):
        if not settings.TELEGRAM_BOT_TOKEN:
            raise CommandError("TELEGRAM_BOT_TOKEN sozlanmagan (.env)")

        url = f"{options['public_base_url'].rstrip('/')}/api/telegram/webhook/{settings.TELEGRAM_WEBHOOK_SECRET}"
        result = TelegramClient().set_webhook(url, secret_token=settings.TELEGRAM_WEBHOOK_SECRET)
        if result.get("ok"):
            self.stdout.write(self.style.SUCCESS(f"Webhook o'rnatildi: {url}"))
        else:
            raise CommandError(f"Webhook o'rnatilmadi: {result}")
