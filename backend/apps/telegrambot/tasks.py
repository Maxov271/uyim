import logging

from celery import shared_task
from django.utils import timezone

from .captions import listing_caption, sold_caption
from .client import TelegramClient

logger = logging.getLogger("uyim.telegram")


@shared_task
def publish_listing_to_channel(listing_id: int):
    from apps.listings.models import Listing

    from .models import TelegramChannel, TelegramPost

    try:
        listing = Listing.objects.select_related("district").get(pk=listing_id)
    except Listing.DoesNotExist:
        return

    channels = TelegramChannel.objects.filter(district_id=listing.district_id, active=True)
    if not channels:
        return

    client = TelegramClient()
    cover = listing.photos.filter(is_cover=True).first() or listing.photos.first()
    caption = listing_caption(listing)

    for channel in channels:
        post, _ = TelegramPost.objects.get_or_create(listing=listing, channel=channel)
        if post.status == TelegramPost.Status.POSTED:
            continue
        target = channel.chat_id or channel.username
        if cover and cover.image:
            result = client.send_photo(target, cover.image.url, caption)
        else:
            result = client.send_message(target, caption)

        if result.get("ok"):
            post.message_id = result["result"]["message_id"]
            post.status = TelegramPost.Status.POSTED
            post.posted_at = timezone.now()
            post.error = ""
        else:
            post.status = TelegramPost.Status.FAILED
            post.error = str(result.get("description") or result.get("error") or "unknown")
        post.save()


@shared_task
def update_listing_posts(listing_id: int):
    """Price changed on an already-published listing — edit the live channel post captions."""
    from apps.listings.models import Listing

    from .models import TelegramPost

    try:
        listing = Listing.objects.select_related("district").get(pk=listing_id)
    except Listing.DoesNotExist:
        return

    client = TelegramClient()
    caption = listing_caption(listing)
    for post in TelegramPost.objects.filter(listing=listing, status=TelegramPost.Status.POSTED):
        target = post.channel.chat_id or post.channel.username
        client.edit_message_caption(target, post.message_id, caption)


@shared_task
def mark_listing_sold(listing_id: int):
    from apps.listings.models import Listing

    from .models import TelegramPost

    try:
        listing = Listing.objects.select_related("district").get(pk=listing_id)
    except Listing.DoesNotExist:
        return

    client = TelegramClient()
    caption = sold_caption(listing_caption(listing))
    for post in TelegramPost.objects.filter(listing=listing, status=TelegramPost.Status.POSTED):
        target = post.channel.chat_id or post.channel.username
        result = client.edit_message_caption(target, post.message_id, caption)
        if result.get("ok"):
            post.status = TelegramPost.Status.SOLD
            post.save(update_fields=["status"])


@shared_task
def notify_owner_new_lead(lead_id: int):
    from apps.leads.models import Lead

    try:
        lead = Lead.objects.select_related("listing", "listing__owner").get(pk=lead_id)
    except Lead.DoesNotExist:
        return

    owner = lead.listing.owner
    if not owner.telegram_id or not owner.notify_telegram:
        return

    channel_label = {"call": "qo'ng'iroq", "chat": "chat", "telegram": "Telegram"}.get(
        lead.channel, lead.channel
    )
    text = (
        f"\U0001f514 Yangi lid! E'loningizga {channel_label} orqali murojaat bo'ldi.\n"
        f"#{lead.listing_id} · {lead.listing.district.name}, {lead.listing.mahalla}"
    )
    TelegramClient().send_message(owner.telegram_id, text)


@shared_task
def notify_saved_searches(listing_id: int):
    """A listing just went active — push it to every SavedSearch whose filters match."""
    from apps.favorites.models import SavedSearch
    from apps.listings.filters import apply_filters
    from apps.listings.models import Listing
    from apps.listings.views import _base_queryset

    try:
        listing = Listing.objects.get(pk=listing_id)
    except Listing.DoesNotExist:
        return

    client = TelegramClient()
    for search in SavedSearch.objects.filter(is_active=True, notify_telegram=True).select_related("user"):
        if not search.user.telegram_id:
            continue
        matches = apply_filters(_base_queryset().filter(pk=listing.pk), search.query)
        if not matches.exists():
            continue
        text = (
            f"\U0001f3e0 “{search.title or 'Saqlangan qidiruv'}” bo'yicha yangi e'lon!\n\n"
            f"{listing_caption(listing)}"
        )
        client.send_message(search.user.telegram_id, text)
        search.last_result_count += 1
        search.last_run_at = timezone.now()
        search.save(update_fields=["last_result_count", "last_run_at"])
