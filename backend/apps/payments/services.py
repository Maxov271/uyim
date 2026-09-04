import base64

from django.conf import settings

from .models import BoostOrder

# Boost package pricing (UZS) — a fixed duration per package; tune freely from admin/config
# later without touching the API contract (POST /api/listings/:id/boost -> {package}).
PACKAGE_PRICE_UZS = {
    BoostOrder.Package.TOP: 50_000,
    BoostOrder.Package.HOT: 30_000,
    BoostOrder.Package.TG_PUSH: 20_000,
    BoostOrder.Package.BANNER: 100_000,
}
PACKAGE_DURATION_DAYS = {
    BoostOrder.Package.TOP: 7,
    BoostOrder.Package.HOT: 3,
    BoostOrder.Package.TG_PUSH: 1,
    BoostOrder.Package.BANNER: 7,
}


def create_boost_order(listing, package: str, provider: str) -> BoostOrder:
    price = PACKAGE_PRICE_UZS[package]
    return BoostOrder.objects.create(
        listing=listing, package=package, provider=provider, price_uzs=price
    )


def build_payment_url(order: BoostOrder) -> str:
    if order.provider == BoostOrder.Provider.CLICK:
        return _click_url(order)
    return _payme_url(order)


def _payme_url(order: BoostOrder) -> str:
    """https://developer.help.paycom.uz/initsializatsiya-platezhey/formirovanie-urla —
    base64("m=<merchant>;ac.order_id=<id>;a=<amount tiyin>")
    """
    if not settings.PAYME_MERCHANT_ID:
        return ""
    amount_tiyin = order.price_uzs * 100
    raw = f"m={settings.PAYME_MERCHANT_ID};ac.order_id={order.id};a={amount_tiyin}"
    token = base64.b64encode(raw.encode()).decode()
    return f"https://checkout.paycom.uz/{token}"


def _click_url(order: BoostOrder) -> str:
    """https://docs.click.uz/click-api-request/ — hosted "Checkout" invoice link."""
    if not settings.CLICK_SERVICE_ID or not settings.CLICK_MERCHANT_ID:
        return ""
    return (
        "https://my.click.uz/services/pay"
        f"?service_id={settings.CLICK_SERVICE_ID}"
        f"&merchant_id={settings.CLICK_MERCHANT_ID}"
        f"&amount={order.price_uzs}"
        f"&transaction_param={order.id}"
    )


def apply_boost(order: BoostOrder):
    """Grants the purchased effect once a payment provider confirms the transaction."""
    from datetime import timedelta

    from django.utils import timezone

    listing = order.listing
    days = PACKAGE_DURATION_DAYS[order.package]
    until = timezone.now() + timedelta(days=days)

    if order.package == BoostOrder.Package.TOP:
        listing.top_until = until
        listing.save(update_fields=["top_until"])
    elif order.package == BoostOrder.Package.HOT:
        listing.hot_until = until
        listing.save(update_fields=["hot_until"])
    elif order.package == BoostOrder.Package.TG_PUSH:
        from apps.telegrambot.tasks import publish_listing_to_channel

        publish_listing_to_channel.delay(listing.id)
    # "banner" is surfaced editorially (homepage placement) — no listing field to flip here.
