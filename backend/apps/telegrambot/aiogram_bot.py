"""Uyim.uz Telegram bot — long polling via aiogram.

Replaces the old webhook receiver (`TelegramWebhookView` in views.py, now unused but kept
for reference) so the bot doesn't depend on Coolify/Telegram webhook delivery at all: this
process calls Telegram's `getUpdates` itself, continuously, for as long as it's running.
Started by `python manage.py run_telegram_bot` (see management/commands/), which
backend/start.sh launches in the background alongside gunicorn — see that file for the
restart-on-crash loop that keeps this "always on".

Behavior mirrors the old webhook handler exactly:
  - /start with no payload → ask for the user's phone via a contact-request keyboard.
  - /start <link_token>    → Telegram-delivered OTP: auth.html's "Telegram orqali kod olish"
                              opens t.me/<bot>?start=<link_token>; deliver the pending
                              OTPCode's code as a chat message instead of SMS.
  - a shared contact       → link phone + telegram_id to a User account (get_or_create),
                              so saved-search pushes / new-lead alerts have somewhere to go.

Outbound-only pushes (saved-search alerts, new-lead alerts, auto-publish — apps/telegrambot/
tasks.py, run from Celery) are unaffected by this file: they still use the synchronous
apps.telegrambot.client.TelegramClient, which only *sends*, never receives.
"""

from __future__ import annotations

import logging

from aiogram import Bot, Dispatcher, F
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import KeyboardButton, Message, ReplyKeyboardMarkup, ReplyKeyboardRemove
from asgiref.sync import sync_to_async
from django.conf import settings

logger = logging.getLogger("uyim.telegram")

CONTACT_KEYBOARD = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="\U0001f4de Telefon raqamni yuborish", request_contact=True)]],
    resize_keyboard=True,
    one_time_keyboard=True,
)


@sync_to_async
def _link_account(telegram_id: int, username: str, raw_phone: str) -> None:
    from django.contrib.auth import get_user_model

    User = get_user_model()
    phone = User.objects.normalize_phone(raw_phone)
    user, _ = User.objects.get_or_create(phone=phone)
    user.telegram_id = telegram_id
    user.telegram_username = username or ""
    user.verified_phone = True
    user.save(update_fields=["telegram_id", "telegram_username", "verified_phone"])


@sync_to_async
def _fetch_pending_otp(link_token: str):
    from apps.accounts.models import OTPCode

    otp = OTPCode.objects.filter(link_token=link_token, channel=OTPCode.Channel.TELEGRAM).first()
    return otp if (otp and otp.is_valid()) else None


@sync_to_async
def _mark_otp_delivered(otp, chat_id: int, username: str) -> None:
    otp.telegram_chat_id = chat_id
    otp.telegram_username = username or ""
    otp.save(update_fields=["telegram_chat_id", "telegram_username"])


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def on_start(message: Message) -> None:
        parts = (message.text or "").split(maxsplit=1)
        link_token = parts[1].strip() if len(parts) > 1 else ""

        if link_token:
            otp = await _fetch_pending_otp(link_token)
            if otp is None:
                await message.answer("Bu havola eskirgan. Ilovaga qaytib, kodni qaytadan so'rang.")
                return
            await _mark_otp_delivered(otp, message.chat.id, message.from_user.username)
            await message.answer(
                f"Uyim.uz tasdiqlash kodingiz: <b>{otp.code}</b>\n"
                f"Kodni ilovaga qaytib kiriting. Hech kimga aytmang.",
                parse_mode=ParseMode.HTML,
            )
            return

        await message.answer(
            "Uyim.uz botiga xush kelibsiz! Hisobingizni ulash uchun telefon raqamingizni yuboring.",
            reply_markup=CONTACT_KEYBOARD,
        )

    @dp.message(F.contact)
    async def on_contact(message: Message) -> None:
        contact = message.contact
        if contact.user_id != message.from_user.id:
            await message.answer("Iltimos, faqat o'zingizning raqamingizni yuboring.")
            return
        await _link_account(message.from_user.id, message.from_user.username, contact.phone_number)
        await message.answer(
            "✅ Hisobingiz ulandi! Endi saqlangan qidiruvlaringiz va yangi lidlar "
            "haqida shu yerga xabar keladi.",
            reply_markup=ReplyKeyboardRemove(),
        )

    @dp.message()
    async def on_fallback(message: Message) -> None:
        await message.answer("Buyruqni tushunmadim. /start bilan boshlang.")

    return dp


async def run_polling() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN sozlanmagan — Telegram bot ishga tushmadi.")
        return

    bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
    dp = build_dispatcher()
    # getUpdates (long polling) and an active webhook are mutually exclusive on
    # Telegram's side — always clear any leftover webhook before polling.
    await bot.delete_webhook(drop_pending_updates=False)
    logger.info("Telegram bot: long polling boshlandi.")
    # start_polling closes the bot's session itself once polling stops.
    await dp.start_polling(bot)
