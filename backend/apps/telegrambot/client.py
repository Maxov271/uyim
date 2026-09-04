"""Thin wrapper over the Telegram Bot API (https://core.telegram.org/bots/api) using plain
HTTP calls — no heavyweight SDK needed for send/edit/webhook operations.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings

logger = logging.getLogger("uyim.telegram")

API_BASE = "https://api.telegram.org/bot{token}"


class TelegramClient:
    def __init__(self, token: str | None = None):
        self.token = token or settings.TELEGRAM_BOT_TOKEN
        self.enabled = bool(self.token)

    def _url(self, method: str) -> str:
        return f"{API_BASE.format(token=self.token)}/{method}"

    def _call(self, method: str, **payload):
        if not self.enabled:
            logger.info("[TG disabled] %s %s", method, payload)
            return {"ok": False, "disabled": True}
        try:
            resp = requests.post(self._url(method), json=payload, timeout=15)
            data = resp.json()
            if not data.get("ok"):
                logger.warning("Telegram API xatosi: %s -> %s", method, data)
            return data
        except Exception:  # noqa: BLE001 — a failed Telegram call must never break the caller
            logger.exception("Telegram API so'rovi muvaffaqiyatsiz: %s", method)
            return {"ok": False, "error": "request_failed"}

    def send_message(self, chat_id, text, reply_markup=None, parse_mode="HTML"):
        payload = {"chat_id": chat_id, "text": text, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._call("sendMessage", **payload)

    def send_photo(self, chat_id, photo_url, caption, reply_markup=None, parse_mode="HTML"):
        payload = {"chat_id": chat_id, "photo": photo_url, "caption": caption, "parse_mode": parse_mode}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self._call("sendPhoto", **payload)

    def edit_message_caption(self, chat_id, message_id, caption, parse_mode="HTML"):
        return self._call(
            "editMessageCaption",
            chat_id=chat_id,
            message_id=message_id,
            caption=caption,
            parse_mode=parse_mode,
        )

    def answer_callback_query(self, callback_query_id, text=None):
        payload = {"callback_query_id": callback_query_id}
        if text:
            payload["text"] = text
        return self._call("answerCallbackQuery", **payload)

    def set_webhook(self, url, secret_token=None):
        payload = {"url": url}
        if secret_token:
            payload["secret_token"] = secret_token
        return self._call("setWebhook", **payload)

    def request_contact_keyboard(self, text="\U0001f4de Telefon raqamni yuborish"):
        return {
            "keyboard": [[{"text": text, "request_contact": True}]],
            "resize_keyboard": True,
            "one_time_keyboard": True,
        }
