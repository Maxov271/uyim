"""Uzbek-language relative time formatting — matches the frontend mock strings
("3 kun oldin", "kecha", …) so the API can drop straight into the existing templates.
"""

from __future__ import annotations

from datetime import datetime

from django.utils import timezone


def time_ago_uz(value: datetime) -> str:
    if value is None:
        return ""
    now = timezone.now()
    delta = now - value
    seconds = int(delta.total_seconds())

    if seconds < 60:
        return "hozirgina"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} daqiqa oldin"
    hours = minutes // 60
    if hours < 24:
        return f"{hours} soat oldin"
    days = hours // 24
    if days == 1:
        return "kecha"
    if days < 7:
        return f"{days} kun oldin"
    weeks = days // 7
    if weeks < 5:
        return f"{weeks} hafta oldin"
    months = days // 30
    if months < 12:
        return f"{months} oy oldin"
    years = days // 365
    return f"{years} yil oldin"
