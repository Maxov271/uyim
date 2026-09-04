"""USD/UZS rate — daily-synced from the Central Bank of Uzbekistan, cached, with the static
settings.USD_UZS_RATE as a safe fallback if the CBU API is unreachable (e.g. offline dev)."""

from __future__ import annotations

import logging

import requests
from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger("uyim.currency")

CACHE_KEY = "usd_uzs_rate"


def get_usd_rate() -> float:
    cached = cache.get(CACHE_KEY)
    return cached if cached else settings.USD_UZS_RATE


def sync_usd_rate() -> float | None:
    try:
        resp = requests.get(settings.CBU_RATE_API, params={"currency": "USD"}, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        rate = float(data[0]["Rate"])
        cache.set(CACHE_KEY, rate, timeout=36 * 3600)
        return rate
    except Exception:  # noqa: BLE001 — a stale cached/fallback rate beats a crashed request
        logger.exception("CBU kursi yangilanmadi")
        return None
