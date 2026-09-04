"""Builds the small activity feed shown on dashboard-buyer.html (D.NOTIFICATIONS in the old
mock) from real state: saved-search hits, price drops on favorites, unread chat replies.
"""

from __future__ import annotations

from datetime import timedelta

from django.utils import timezone

from apps.core.humanize_uz import time_ago_uz


def build_notifications(user, limit: int = 8) -> list[dict]:
    if not user or not user.is_authenticated:
        return []

    items = []

    for search in user.saved_searches.filter(is_active=True, last_result_count__gt=0).order_by(
        "-last_run_at"
    )[:5]:
        items.append(
            {
                "icon": "ph-bell-ringing",
                "text": f"“{search.title or 'Saqlangan qidiruv'}” qidiruvi bo'yicha "
                f"{search.last_result_count} yangi e'lon",
                "time": time_ago_uz(search.last_run_at),
                "_at": search.last_run_at,
            }
        )

    since = timezone.now() - timedelta(days=3)
    for fav in user.favorites.select_related("listing").filter(listing__price_history__changed_at__gte=since):
        history = list(fav.listing.price_history.order_by("changed_at"))
        if len(history) < 2:
            continue
        drop = history[-2].price_usd - history[-1].price_usd
        if drop <= 0:
            continue
        items.append(
            {
                "icon": "ph-trend-down",
                "text": f"Saqlangan e'lon narxi {int(drop):,} $ tushdi — {fav.listing.mahalla}, "
                f"{fav.listing.rooms} xona".replace(",", " "),
                "time": time_ago_uz(history[-1].changed_at),
                "_at": history[-1].changed_at,
            }
        )

    from apps.leads.models import ChatMessage

    unread = (
        ChatMessage.objects.filter(thread__buyer=user, read_at__isnull=True)
        .exclude(sender=user)
        .select_related("thread", "sender")
        .order_by("-created_at")[:5]
    )
    for msg in unread:
        items.append(
            {
                "icon": "ph-chat-circle-dots",
                "text": f"{msg.sender.name or msg.sender.phone} chatda javob berdi",
                "time": time_ago_uz(msg.created_at),
                "_at": msg.created_at,
            }
        )

    items.sort(key=lambda x: x["_at"], reverse=True)
    for item in items:
        item.pop("_at")
    return items[:limit]
