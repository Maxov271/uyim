from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .client import TelegramClient

User = get_user_model()


class TelegramWebhookView(APIView):
    """Receives Telegram Bot API updates (https://core.telegram.org/bots/api#update).

    SUPERSEDED: the bot now runs continuously via long polling — see
    apps.telegrambot.aiogram_bot / `python manage.py run_telegram_bot` (started by
    backend/start.sh alongside gunicorn) — so no webhook is registered anymore and
    Telegram never calls this endpoint. Kept only as a reference/fallback; the logic
    below is duplicated (by design, not by import) in aiogram_bot.py's handlers.

    Implements the MVP flow from CLAUDE_CODE_PROMPT.md §6: /start asks for a phone number
    via a contact-request keyboard, then links the shared contact to a User account so
    saved-search pushes and new-lead alerts (see telegrambot/tasks.py) have somewhere to go.

    Also implements Telegram-delivered OTP login: auth.html's "Telegram orqali kod olish"
    opens https://t.me/<bot>?start=<link_token> — Telegram passes that token straight through
    as the /start payload, so /start <token> here looks up the pending OTPCode and delivers
    the code as a chat message instead of SMS (see apps/accounts/views.py OTPRequestView /
    OTPVerifyView for the other half of this flow).
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
            payload = text[len("/start"):].strip()
            if payload and self._deliver_otp(client, chat_id, from_user, payload):
                return
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

    def _deliver_otp(self, client: TelegramClient, chat_id, from_user: dict, link_token: str) -> bool:
        from apps.accounts.models import OTPCode

        otp = OTPCode.objects.filter(link_token=link_token, channel=OTPCode.Channel.TELEGRAM).first()
        if not otp or not otp.is_valid():
            client.send_message(
                chat_id, "Bu havola eskirgan. Ilovaga qaytib, kodni qaytadan so'rang."
            )
            return True

        otp.telegram_chat_id = chat_id
        otp.telegram_username = from_user.get("username", "")
        otp.save(update_fields=["telegram_chat_id", "telegram_username"])

        client.send_message(
            chat_id,
            f"Uyim.uz tasdiqlash kodingiz: <b>{otp.code}</b>\nKodni ilovaga qaytib kiriting. "
            f"Hech kimga aytmang.",
        )
        return True
