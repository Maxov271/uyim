"""Query-param filtering/sorting for GET /api/listings — see CLAUDE_CODE_PROMPT.md §5 for the
full contract. Implemented as plain Q-object composition rather than django-filter because a
few params (rooms CSV with a "4+" bucket, lat/lng/radius, sort aliases) don't fit a declarative
FilterSet cleanly.
"""

from __future__ import annotations

from django.db.models import Q, QuerySet

from apps.core.geo_utils import haversine_m

from .models import Listing

SORT_MAP = {
    "new": "-published_at",
    "cheap": "price_usd",
    "rich": "-price_usd",
    "pop": "-views",
}


def _to_bool(v: str | None):
    if v is None:
        return None
    return v.lower() in ("1", "true", "yes")


def apply_filters(qs: QuerySet, params) -> QuerySet:
    deal = params.get("deal")
    if deal:
        qs = qs.filter(deal=deal)

    district = params.get("district")
    if district:
        qs = qs.filter(district_id=district)

    city = params.get("city")
    if city:
        qs = qs.filter(city_id=city)

    mahalla = params.get("mahalla")
    if mahalla:
        qs = qs.filter(mahalla__iexact=mahalla)

    price_min = params.get("price_min")
    if price_min:
        qs = qs.filter(price_usd__gte=price_min)
    price_max = params.get("price_max")
    if price_max:
        qs = qs.filter(price_usd__lte=price_max)

    rooms = params.get("rooms")
    if rooms:
        room_q = Q()
        for raw in rooms.split(","):
            raw = raw.strip()
            if not raw.isdigit():
                continue
            n = int(raw)
            room_q |= Q(rooms__gte=4) if n >= 4 else Q(rooms=n)
        if room_q:
            qs = qs.filter(room_q)

    area_min = params.get("area_min")
    if area_min:
        qs = qs.filter(area__gte=area_min)
    area_max = params.get("area_max")
    if area_max:
        qs = qs.filter(area__lte=area_max)

    floor_min = params.get("floor_min")
    if floor_min:
        qs = qs.filter(floor__gte=floor_min)

    prop_type = params.get("type")
    if prop_type:
        qs = qs.filter(type=prop_type)

    condition = params.get("condition")
    if condition:
        qs = qs.filter(condition=condition)

    verified = _to_bool(params.get("verified"))
    if verified is not None:
        qs = qs.filter(verified_owner=verified)

    mortgage = _to_bool(params.get("mortgage"))
    if mortgage is not None:
        qs = qs.filter(mortgage_allowed=mortgage)

    tg = _to_bool(params.get("tg"))
    if tg is not None:
        qs = qs.filter(tg_posted_count__gt=0) if tg else qs.filter(tg_posted_count=0)

    q_text = params.get("q")
    if q_text:
        qs = qs.filter(
            Q(title__icontains=q_text) | Q(description__icontains=q_text) | Q(mahalla__icontains=q_text)
        )

    sort = params.get("sort", "new")
    qs = qs.order_by(SORT_MAP.get(sort, "-published_at"))

    return qs


def apply_radius(items: list[Listing], lat: float, lng: float, radius_m: float) -> list[Listing]:
    return [it for it in items if haversine_m(lat, lng, it.lat, it.lng) <= radius_m]
