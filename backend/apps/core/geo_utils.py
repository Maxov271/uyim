"""Plain lat/lng geo helpers — Haversine distance, bbox, coarse grid clustering.

No PostGIS/GDAL dependency; portable across SQLite (dev) and Postgres (prod). See the note
in config/settings.py for the upgrade path if the catalogue grows large enough to need a
real spatial index.
"""

from __future__ import annotations

import math
from collections import defaultdict

EARTH_RADIUS_M = 6_371_000


def haversine_m(lat1: float, lng1: float, lat2: float, lng2: float) -> float:
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    a = math.sin(dphi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2
    return 2 * EARTH_RADIUS_M * math.asin(math.sqrt(a))


def jitter_point(lat: float, lng: float, listing_id, max_offset_m: float = 150.0):
    """Deterministic pseudo-random offset so a listing's approximate pin is stable across
    requests but never reveals the exact address — required by CLAUDE_CODE_PROMPT.md §10.
    """
    seed = int(hashlib_digest(listing_id), 16)
    angle = (seed % 360) * math.pi / 180
    dist = max_offset_m * ((seed // 360) % 100) / 100
    dlat = (dist * math.cos(angle)) / 111_320
    dlng = (dist * math.sin(angle)) / (111_320 * math.cos(math.radians(lat)) or 1)
    return round(lat + dlat, 6), round(lng + dlng, 6)


def hashlib_digest(value) -> str:
    import hashlib

    return hashlib.md5(str(value).encode()).hexdigest()[:8]


def bbox_of(points: list[tuple[float, float]]):
    if not points:
        return None
    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]
    return {"south": min(lats), "west": min(lngs), "north": max(lats), "east": max(lngs)}


def cluster_points(items, precision: int = 3):
    """Grid-cluster (lat, lng, payload) tuples by rounding coordinates. `precision=3` groups
    points within roughly ~100m of each other — good enough for a marker-cluster style map
    without a spatial index.
    """
    buckets: dict[tuple[float, float], list] = defaultdict(list)
    for lat, lng, payload in items:
        key = (round(lat, precision), round(lng, precision))
        buckets[key].append(payload)

    clusters = []
    for (lat, lng), payloads in buckets.items():
        clusters.append({"lat": lat, "lng": lng, "count": len(payloads)})
    return clusters
