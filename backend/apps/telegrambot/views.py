from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import TelegramClient

User = get_user_model()


class TelegramWebhookView(APIView):
    """Receives Telegram Bot API updates (https://core.telegram.org/bots/api#update).

    Implements the MVP flow from CLAUDE_CODE_PROMPT.md §6: /start asks for a phone number
    via a contact-request keyboard, then links the shared contact to a User account so
    saved-search pushes and new-lead alerts (see telegrambot/tasks.py) have somewhere to go.
    """

    permission_classes = [permissions.AllowAny]

    def post(self, request, secret: str):
        if secret != settings.TELEGRAM_WEBHOOK_SECRET:
            return Response(status=status.HTTP_403_FORBIDDEN)

        update = request.data
        client = TelegramClient()

        message = update.get("message")
        if message:
            self._handle_message(client, message)

        callback_query = update.get("callback_query")
        if callback_query:
            client.answer_callback_query(callback_query["id"])

        return Response({"ok": True})

    def _handle_message(self, client: TelegramClient, message: dict):
        chat_id = message["chat"]["id"]
        from_user = message.get("from", {})

        if message.get("contact"):
            contact = message["contact"]
            if contact.get("user_id") != from_user.get("id"):
                client.send_message(chat_id, "Iltimos, faqat o'zingizning raqamingizni yuboring.")
                return
            phone = User.objects.normalize_phone(contact["phone_number"])
            user, _ = User.objects.get_or_create(phone=phone)
            user.telegram_id = from_user.get("id")
            user.telegram_username = from_user.get("username", "")
            user.verified_phone = True
            user.save(update_fields=["telegram_id", "telegram_username", "verified_phone"])
            client.send_message(
                chat_id,
                "✅ Hisobingiz ulandi! Endi saqlangan qidiruvlaringiz va yangi lidlar "
                "haqida shu yerga xabar keladi.",
            )
            return

        text = (message.get("text") or "").strip()
        if text.startswith("/start"):
            client.send_message(
                chat_id,
                "Uyim.uz botiga xush kelibsiz! Hisobingizni ulash uchun telefon raqamingizni yuboring.",
                reply_markup=client.request_contact_keyboard(),
            )
            return

        client.send_message(
            chat_id,
            "Buyruqni tushunmadim. /start bilan boshlang.",
        )
