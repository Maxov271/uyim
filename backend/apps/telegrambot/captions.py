from apps.core.humanize_uz import time_ago_uz  # noqa: F401 (available for future caption use)


def listing_caption(listing) -> str:
    parts = [f"<b>{'$' + format(listing.price_usd, ',.0f')}</b>"]
    if listing.rooms:
        parts.append(f"{listing.rooms} xona")
    parts.append(f"{listing.area} m²")
    if listing.floors:
        parts.append(f"{listing.floor}/{listing.floors} qavat")
    line1 = " · ".join(parts)

    line2 = f"{listing.district.name}, {listing.mahalla} mahallasi"
    trust = "✅ Tasdiqlangan egasi" if listing.verified_owner else ""

    lines = [line1, line2]
    if trust:
        lines.append(trust)
    lines.append(f"\n#{listing.district_id} #{listing.deal}")
    return "\n".join(lines)


def sold_caption(caption: str) -> str:
    return f"✅ <b>SOTILDI</b>\n\n{caption}"
