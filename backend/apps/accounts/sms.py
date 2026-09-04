"""SMS OTP delivery via Eskiz.uz (https://eskiz.uz/). Falls back to a console/log-only mode
when no credentials are configured, so local development never needs a real SMS account —
the OTP is echoed back in the API response (DEBUG only) and logged.
"""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("uyim.sms")

ESKIZ_BASE = "https://notify.eskiz.uz/api"
TOKEN_CACHE_KEY = "eskiz:token"


def _eskiz_token() -> str | None:
    token = cache.get(TOKEN_CACHE_KEY)
    if token:
        return token
    if not (settings.ESKIZ_EMAIL and settings.ESKIZ_PASSWORD):
        return None
    try:
        resp = requests.post(
            f"{ESKIZ_BASE}/auth/login",
            data={"email": settings.ESKIZ_EMAIL, "password": settings.ESKIZ_PASSWORD},
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json()["data"]["token"]
        cache.set(TOKEN_CACHE_KEY, token, timeout=25 * 24 * 3600)
        return token
    except Exception:  # noqa: BLE001 — SMS delivery must never crash the request
        logger.exception("Eskiz.uz auth muvaffaqiyatsiz")
        return None


def send_otp_sms(phone: str, code: str) -> bool:
    text = f"Uyim.uz tasdiqlash kodi: {code}. Hech kimga aytmang."
    if not (settings.ESKIZ_EMAIL and settings.ESKIZ_PASSWORD):
        logger.info("[DEV OTP] %s -> %s", phone, code)
        return True

    token = _eskiz_token()
    if not token:
        logger.warning("Eskiz token yo'q, SMS yuborilmadi: %s", phone)
        return False
    try:
        resp = requests.post(
            f"{ESKIZ_BASE}/message/sms/send",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "mobile_phone": phone.lstrip("+"),
                "message": text,
                "from": settings.ESKIZ_FROM,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return True
    except Exception:  # noqa: BLE001
        logger.exception("Eskiz.uz SMS yuborilmadi: %s", phone)
        return False
