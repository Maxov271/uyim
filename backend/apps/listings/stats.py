"""Real analytics computed from live Listing data — replaces the hardcoded DISTRICT_STATS
mock in frontend/assets/js/data.js with numbers derived from what's actually in the catalogue.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from django.db.models import Avg, F
from django.utils import timezone

from .models import Listing


def district_ppm(district_id: str) -> float:
    """Average USD price per m² across active sale/new listings in a district."""
    avg = (
        Listing.objects.filter(
            district_id=district_id, status=Listing.Status.ACTIVE, deal__in=["sale", "new"]
        )
        .annotate(ppm=F("price_usd") / F("area"))
        .aggregate(v=Avg("ppm"))["v"]
    )
    return round(float(avg), 1) if avg else 0.0


def district_stats(limit: int = 8) -> list[dict]:
    from apps.geo.models import District

    now = timezone.now()
    month_ago = now - timedelta(days=30)
    two_months_ago = now - timedelta(days=60)

    rows = []
    for district in District.objects.all()[:limit]:
        current = district_ppm(district.id)

        prev_avg = (
            Listing.objects.filter(
                district_id=district.id,
                status=Listing.Status.ACTIVE,
                deal__in=["sale", "new"],
                created_at__gte=two_months_ago,
                created_at__lt=month_ago,
            )
            .annotate(ppm=F("price_usd") / F("area"))
            .aggregate(v=Avg("ppm"))["v"]
        )
        prev = round(float(prev_avg), 1) if prev_avg else current

        delta = round(((current - prev) / prev) * 100, 1) if prev else 0.0
        supply = Listing.objects.filter(district_id=district.id, status=Listing.Status.ACTIVE).count()

        rows.append({"district": district.name, "ppm": current, "delta": delta, "supply": supply})
    return rows


def month_label_uz(dt) -> str:
    months = [
        "Yan", "Fev", "Mar", "Apr", "May", "Iyn",
        "Iyl", "Avg", "Sen", "Okt", "Noy", "Dek",
    ]
    return months[dt.month - 1]
